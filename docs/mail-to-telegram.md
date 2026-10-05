# Contact Mail To Telegram

This manual gives a product a working `hello@example.com` without a mailbox, a mail provider or a mail server to operate. A small receive-only SMTP service runs on the production host. It accepts mail for a short list of addresses and forwards each message to the owner's Telegram chat. It sends nothing, stores nothing and has no queue.

It fits a prototype or a small product: a contact address on the landing page, `support@` in the legal texts, `security@` in `security.txt`. It does not fit a team that needs shared mailboxes, search or replies from the same address. Section 9 says what to add when that day comes.

## The Shape

```
sender's mail server ── TCP 25 ──▶ host :25 ──▶ container :2525
                                      │ EHLO, STARTTLS (self-signed, optional)
                                      │ RCPT TO   ── not on the list? 550
                                      │ DATA      ── over the size limit? 552
                                      │ parse text (HTML → text), count attachments
                                      │ SPF + DKIM + DMARC ── a label, never a refusal
                                      ▼
                               Telegram sendMessage ── failed or slow? 451, the sender retries
                                      │ ok
                                      ▼
                               250 to the sender, one structured log line
```

| Part | What it is |
| --- | --- |
| Service | One compose service, about 500 lines of Node on three libraries |
| State | None. Read-only file system, no queue, no database |
| Delivery guarantee | The sender hears `250` only after Telegram accepted the text |
| Addresses | An allow-list in one environment variable |
| DNS | An `A` record for the mail host, one `MX`, SPF and DMARC for a domain that sends nothing |
| Cost | About 85 MB of memory idle, a tenth of a CPU core |

## Why Receive-Only, And Why On Your Own Host

Sending and receiving are different problems. Do not let the first decide the second.

| | Receiving | Sending |
| --- | --- | --- |
| What decides success | An `MX` record and an open port 25 | The reputation of your IP and domain |
| Reverse DNS (PTR) | Irrelevant: nobody checks the PTR of an MX before delivering to it | Required |
| DKIM key of your own | Not needed | Required |
| A fresh cloud IP | Works on the first day | Often lands in spam, and many clouds block outgoing 25 |

So receive on your own host, where it is easy and private. When you need to send, use a transactional provider over HTTPS. A full mail server (Postfix, Maddy, Stalwart, docker-mailserver) solves both at once and brings a queue, mailboxes and a delivery path you then have to keep closed. For a contact address that is hundreds of megabytes guarding against a problem you do not have.

Off-the-shelf SMTP-to-Telegram bridges exist. Read their source before putting one on a public port. The common ones are written as notification sinks for a private network: they accept any recipient, offer no TLS and forward attachments. On port 25 of the internet that is an open sink with your bot token beside it.

## 1. The Service

Use [`smtp-server`](https://github.com/nodemailer/smtp-server) for the protocol, [`mailparser`](https://github.com/nodemailer/mailparser) for MIME and [`mailauth`](https://github.com/postalsys/mailauth) for sender authentication. Do not write SMTP or MIME by hand. Real mail arrives as nested multipart in `koi8-r` with RFC 2047 headers, and a hand-written parser on a public port is a worse bet than three pinned packages.

Pin exact versions with a lockfile. Install with `npm ci --omit=dev --ignore-scripts`. Keep the service out of the application's workspace so its dependency tree ships only in its own image.

The whole behaviour sits in four hooks:

```js
const server = new SMTPServer({
  authOptional: true,
  disabledCommands: ["AUTH"],          // nobody logs in; nothing is relayed
  name: config.hostname,               // mx.example.com
  key: tls.key, cert: tls.cert,        // self-signed, made at start
  size: config.maxBytes,               // announced in EHLO as SIZE
  maxClients: 20,
  socketTimeout: 60_000,

  onConnect(session, done) {           // per-address connection limits
    done(tooMany(session.remoteAddress) ? smtpError(421, "4.7.0 Try again later") : undefined);
  },

  onRcptTo(address, session, done) {   // the allow-list is the whole policy
    if (config.recipients.includes(address.address.toLowerCase())) return done();
    done(smtpError(550, "5.7.1 This server accepts mail for its own addresses only"));
  },

  onData(stream, session, done) {
    receive(stream, session)           // parse + authenticate + send to Telegram
      .then(() => done(null, "2.0.0 Message accepted"))
      .catch((error) => done(error.responseCode ? error : smtpError(451, "4.3.0 Try again later")));
  },
});
```

Rules the implementation must keep:

1. **Answer `250` only after Telegram accepted the message.** Any Telegram failure, timeout or rate limit becomes `451`. The sending server keeps the mail and retries for days. That retry is your queue. The one cost: if the connection breaks after Telegram accepted and before the `250` arrived, you see the message twice.
2. **Reject unknown recipients at `RCPT`, with `550`.** Exact match against the list, no wildcards. Tell a missing local mailbox (`5.1.1`) from a relay attempt (`5.7.1`) in the text if you like; both are refusals. The service has no outbound SMTP code, so "never an open relay" is a fact about the code, not a setting.
3. **Send plain text to Telegram.** No `parse_mode`, link previews off. Then nothing in a mail can become formatting, a mention or a link target. Strip control characters and Unicode bidirectional overrides from every field.
4. **Do not forward attachments in the first version.** List their names and sizes. Stream the bytes past the parser and drop them, so a 10 MB attachment does not cost 10 MB of memory.
5. **Show the SMTP recipient, not the `To:` header.** A Bcc or a list copy is then shown by the address that actually received it.
6. **Cut the text to Telegram's 4096 characters with a visible marker** that says how much was shown.
7. **Log one structured line per message**: sender, recipient, size, outcome, client address, authentication results. Never a body, never the token. Scrub the token out of error text before logging it: a failed `fetch` can carry the URL.

## 2. Sender Authentication Is A Label

Check SPF, DKIM and DMARC on every accepted message and show the verdict as one line in the Telegram text. Never refuse or defer mail because of it. This is a contact mailbox: the owner wants to see everything, honestly labelled.

| Line | When |
| --- | --- |
| `Authenticity: confirmed (DMARC pass; SPF pass, DKIM pass: example.org)` | DMARC passed. SPF alone never confirms |
| `⚠ Authenticity: NOT CONFIRMED — may be forged (DMARC fail; …)` | The domain publishes DMARC and the message does not satisfy it |
| `Authenticity: undetermined — the sender's domain has no DMARC (…)` | No DMARC record. Say what SPF and DKIM gave and leave the verdict open |
| `Authenticity: not checked (DNS error)` | A lookup failed or timed out, or the library threw |

Details that matter:

- **Keep the four states distinct.** A failure that came with a DNS error is "not checked", not "forged".
- **Bound the DNS.** A few seconds per lookup and about ten seconds for the whole check, counted from the last byte of the message. A slow resolver must not hold the SMTP transaction past the sender's patience.
- **A failed check still delivers.** Wrap the whole authentication in a catch that yields "not checked".
- **Feed `mailauth` the stream.** It hashes the body incrementally and keeps only the headers. Feed the MIME parser a capped prefix of the same stream (the first 4 MB is plenty for the text). The two readers need backpressure between them, or the faster one buffers the message for the slower.
- **Inject the resolver.** `mailauth` takes a `resolver` function. Tests then run offline with a fake DNS, and production wraps Node's resolver with the timeouts.

Do not skip this to save memory. The library costs about 35 MB resident. Raise the container limit instead.

## 3. Limits For A Public Port

Port 25 is probed from the first minute. Keep every limit in memory and let a restart forget them.

| Limit | A value that works |
| --- | --- |
| Message size | 10 MB in `SIZE`. Past it, read and drop the bytes, then `552` |
| Parsed prefix | The first 4 MB. A larger message is delivered with a line saying the text may be incomplete |
| Messages in flight | 1. A second `DATA` gets `451` and the sender retries |
| Connections | 20 in total, 3 per address, 20 new per address per minute |
| Messages | 30 per address per hour |
| Unknown recipients | The third in one session closes it. Ten from one address in an hour refuses that address at connect |
| Idle | 60 s without a byte |
| Whole session | 5 minutes, however slowly the bytes trickle. The idle timeout alone resets on every byte |

No spam filter. SpamAssassin, rspamd and ClamAV are each heavier than the whole service. The allow-list and the limits are the filter, and some spam to `hello@` will reach Telegram.

## 4. The Container

```yaml
inbound-mail:
  build:
    context: ./inbound-mail
  environment:
    INBOUND_MAIL_RECIPIENTS: ${INBOUND_MAIL_RECIPIENTS:-hello@example.com,support@example.com,security@example.com}
    INBOUND_MAIL_HOSTNAME: mx.example.com
    INBOUND_MAIL_CHAT_ID: ${OWNER_CHAT_ID}
    TELEGRAM_BOT_TOKEN: ${TELEGRAM_BOT_TOKEN}
  ports:
    - "25:2525"          # the process is not root and cannot bind 25 itself
  read_only: true
  cap_drop: [ALL]
  security_opt: ["no-new-privileges:true"]
  cpus: "0.1"
  mem_limit: 256m
  healthcheck:
    test: ["CMD", "bash", "-c", "exec 3<>/dev/tcp/127.0.0.1/2525 && read -t 5 line <&3 && echo QUIT >&3 && [[ $$line == 220* ]]"]
```

- **Self-signed certificate, generated at start.** Inbound STARTTLS is opportunistic (RFC 7435): senders encrypt but do not validate, so nothing needs renewing. Generate it with `node:crypto`; the slim Node image has no `openssl`. A real certificate matters only if you later publish MTA-STS.
- **Do not refuse plaintext.** Some senders cannot negotiate TLS, and refusing them loses mail.
- **Health check without a second Node process.** A bash `/dev/tcp` probe costs nothing. A Node one-liner every 30 seconds costs 40 MB each time.
- **Exempt 127.0.0.1 from the per-address limits**, or the health check locks the service out of itself.
- **Cap the heap below the container limit** (`--max-old-space-size=160` under 256 MB) so V8 collects before the kernel kills.
- **Handle `SIGTERM`.** Node as PID 1 ignores it by default and Docker waits ten seconds before killing.

Measured with these flags on Node 24: 85 MB idle, a plateau of 126–136 MB after a run of 10 MB messages, 150 MB peak. A 10 MB signed message takes 4.5–13 s at a tenth of a core, inside the idle timeout.

## 5. DNS

| Name | Type | Value | Why |
| --- | --- | --- | --- |
| `mx.example.com` | A | the host's address | The mail host gets its own name, so it can move without touching the site's record |
| `example.com` | MX | `10 mx.example.com.` | Where senders deliver. An MX must name a host with an address record, never a CNAME (RFC 2181 §10.3) |
| `example.com` | TXT | `v=spf1 -all` | No server may send as this domain |
| `_dmarc.example.com` | TXT | `v=DMARC1; p=reject; sp=reject; adkim=s; aspf=s` | Receivers that honour DMARC drop anything claiming to be you |

One MX is enough. When the host is down, senders queue and retry for days. A secondary MX is a second place to lose mail.

SPF and DMARC for a domain that sends nothing are what stop a stranger from sending as `hello@example.com`. Publish them even though this service never sends.

A name has exactly one TXT record set. If the apex already holds ownership tokens (search consoles, a site verification), add SPF to that same set. A second `v=spf1` record makes both invalid.

Leave `rua` out of DMARC while the only mailbox turns mail into Telegram messages. Aggregate reports would arrive as daily noise.

## 6. Three Firewalls

A published Docker port passes three independent layers. Missing one looks exactly like "the provider blocks port 25".

1. **The cloud security group**: TCP 25 from anywhere. A sending server cannot be allow-listed in advance.
2. **The host firewall** (`ufw allow 25/tcp`).
3. **The `DOCKER-USER` chain**, if you keep a default-drop backstop there. Docker publishes by DNAT, which bypasses `ufw`, so the backstop needs its own rule: `--ctorigdstport 25 -j RETURN` before the final `DROP`.

Many clouds block **outgoing** 25, 465 and 587 and leave inbound open. Read your provider's page on blocked ports, then measure instead of trusting it.

If the firewall is set by cloud-init, remember that it runs only when a host is created. Put the rule in the template for the next host and apply it by hand on the live one.

## 7. Tests

Test against a real SMTP session on `127.0.0.1` with an ephemeral port, a fake Telegram endpoint and a fake DNS resolver. No network, no mocks of the SMTP library itself.

Cover at least:

- an allowed recipient is accepted; an unknown local one and a foreign one are both `550`;
- a message over the size limit is `552`;
- Telegram answering 500, 429 or nothing gives `451`, and no `250` is ever sent before Telegram accepted;
- HTML-only mail becomes text; an attachment is listed and not forwarded;
- truncation at the Telegram limit carries the marker and never splits a surrogate pair;
- DMARC pass through DKIM (sign a message in the test with a generated key), pass through aligned SPF, fail, a body tampered after signing, no DMARC record, a resolver that throws;
- a message larger than the parsed prefix is still authenticated over its whole body;
- no log line contains a body or the token.

Then build the image and run it once under the production flags with large messages. The memory numbers in section 4 came from that run, and an earlier version was OOM-killed there, not in the tests.

## 8. Roll Out And Verify

Order matters: open the firewall and publish DNS first, deploy second, advertise the address last.

```bash
nc -v mx.example.com 25                                              # 220 mx.example.com ESMTP …
openssl s_client -connect mx.example.com:25 -starttls smtp -crlf </dev/null | head
swaks --to hello@example.com   --from you@example.org --server mx.example.com --tls-optional
swaks --to someone@gmail.com   --from you@example.org --server mx.example.com --quit-after RCPT   # must be 550
swaks --to nobody@example.com  --from you@example.org --server mx.example.com --quit-after RCPT   # must be 550
dig +short MX example.com @1.1.1.1
```

Then write to the address from a Gmail account. That is the test that matters: Gmail finds the server through the MX record, so it checks the DNS as well as the service, and its message should show `Authenticity: confirmed`.

Check once, on the first real message:

- **The client address in the log is the sender's, not `172.x`.** If it is the Docker gateway, every per-address limit applies to all senders together.
- **The verdict line appears.** It proves DNS works from inside the container.

Only now put the address on the site. A contact address that bounces for an afternoon is worse than none.

## 9. When You Need To Send

This service cannot send, and the DNS in section 5 forbids anyone to. To reply from `hello@example.com`:

1. Pick a transactional provider with an HTTPS API (Postmark, SES, Resend, Mailgun). It avoids the blocked outgoing ports and the reputation of a fresh cloud IP.
2. Replace `v=spf1 -all` with the provider's `include:`. Still exactly one SPF record.
3. Publish the provider's DKIM records (`selector._domainkey`).
4. Relax DMARC to `p=quarantine` while testing, add a `rua` that someone reads, then return to `p=reject`.
5. A PTR record is needed only if mail leaves from your own host.

Inbound stays as it is. The two paths do not share anything.

## Pitfalls Met In Practice

- **Testing your own limits locks you out.** A script that polled `RCPT TO` for an address not yet deployed was treated as a prober and refused at connect for an hour. The limits worked. Poll with an address that already exists, or from the host's loopback.
- **`/dev/tcp` is a bash feature.** A wait loop written with it under zsh never succeeds. Make the shell explicit in scripts that probe ports.
- **Home networks block outgoing 25.** A timeout from a laptop proves nothing about the server. Probe from a few outside locations before blaming the provider.
- **A memory limit copied from a neighbour.** The first version skipped sender authentication to fit a 96 MB limit borrowed from a 60-line notifier. The host had gigabytes free. Size the limit from a measurement of this service, not from the service next to it.
- **A parser that reads everything.** Letting the MIME parser read a 10 MB text-only message got the container killed. Cap what the parser sees and keep one message in flight.
- **`postmaster@` and `abuse@`.** RFC 5321 expects a receiving domain to accept `postmaster`, and other operators send abuse reports to `abuse@`. Both attract spam. Add them when the product is large enough to care.

## Sources

- [`smtp-server`](https://github.com/nodemailer/smtp-server), [`mailparser`](https://github.com/nodemailer/mailparser), [`mailauth`](https://github.com/postalsys/mailauth)
- [Telegram Bot API: sendMessage](https://core.telegram.org/bots/api#sendmessage)
- RFC 5321 (SMTP, retry, `postmaster`), RFC 2181 §10.3 (an MX target is not an alias), RFC 7435 (opportunistic security), RFC 7489 (DMARC), RFC 9116 (`security.txt`)
