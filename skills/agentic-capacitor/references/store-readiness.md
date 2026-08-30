# Store readiness during web-app conversion

Read when store distribution affects product architecture. Recheck current policy, storefront, distribution channel and exceptions at design and submission time; this is a decision checklist, not legal advice or a guarantee of review acceptance. Do not carry Apple-specific rules over to Android unexamined.

## Product and login

Apple guideline 4.2 evaluates usefulness, content and app experience beyond a repackaged website. There is no fixed native-plugin quota. Choose sharing, camera, notifications, haptics or other features only where they serve the product; decorative additions do not guarantee approval.

For third-party/social login to the primary account, assess guideline 4.8 and its exceptions. Sign in with Apple is a common way to offer the required equivalent privacy-preserving option, not an unconditional requirement for every app with authentication. A first-party-only login system and qualifying enterprise/education cases differ. Source: [App Review Guidelines, 4.2 and 4.8](https://developer.apple.com/app-store/review/guidelines/).

Design the native auth return and relevant deep-link routes before the first distribution trial, using the existing auth-network reference. Custom schemes versus universal links depend on the provider-supported flow; universal links are not a universal replacement for native OAuth session APIs. Test email/magic/password-reset/invitation links when those features exist.

## Account deletion

If the app supports account creation, provide an in-app way to initiate account deletion, including when signup is offered through a linked website. Model real deletion rather than only deactivation, with appropriate reauthentication, session/token revocation, retention disclosures and completion/error states. Ordinary apps should not force email/phone support as the only route; Apple's guidance describes limited regulated-industry exceptions. Explain subscription management separately from account deletion; do not promise a refund or cancellation merely because the account is removed. Source: [Apple account-deletion guidance](https://developer.apple.com/support/offering-account-deletion-in-your-app/).

Reuse the backend's authorized deletion workflow; its URL or HTTP verb is an implementation choice. Never invoke deletion against a real user while preparing or testing the integration without authorization.

For Google Play, an app that supports account creation generally needs both an in-app deletion path and an external web resource for requesting account/associated-data deletion, plus the appropriate Data safety disclosures. The Apple-only path above does not complete this requirement. Keep the external resource usable after uninstall and explain legitimate retention. Source: [Google Play account deletion](https://support.google.com/googleplay/android-developer/answer/13327111).

## Digital purchases and entitlements

Classify digital goods/features, physical services, existing cross-platform subscriptions and relevant storefront rules before retaining a web checkout link inside the app. Consult applicable IAP/StoreKit and external-purchase exceptions; neither “Stripe always works” nor “external checkout is universally forbidden” is a safe global rule. Source: [Apple business models](https://developer.apple.com/app-store/business-models/).

Keep backend entitlement decisions independent of a single payment provider. Track provider/source, product and ownership, verification, expiry, revocation/refunds and restoration; reconcile server events idempotently. Never grant durable access from an unverified client flag or purchase callback. Preserve existing web entitlements when implementing a new store channel, subject to the applicable product/store rules.

Assess Google Play's payments policy separately, including distribution/program/country exceptions and the supported billing-library requirement for the chosen plugin. Verify acknowledgement, pending/cancelled purchases, restore/query and server-side entitlement reconciliation for that provider. Do not transplant a StoreKit callback contract or Apple storefront exception into Android. Sources: [Google Play payments policy](https://support.google.com/googleplay/android-developer/answer/9858738?hl=en-GB), [Play Billing integration](https://developer.android.com/google/play/billing/integrate).

## Privacy and acceptance evidence

Use the security reference for manifests, listed SDKs, signing conditions and required-reason APIs. Keep store disclosures consistent with actual SDK collection. Provide an actionable checklist of applicable requirements, evidence and unresolved decisions rather than a blanket “store-ready” claim. Preparing a submission does not authorize submitting it.

## Apple release-review handoff

For an Apple submission, resubmission or rejection, the optional companion [apple-app-store-reviewer](https://github.com/CodeAlive-AI/vibe-stack/blob/main/skills/apple-app-store-reviewer/SKILL.md) covers the exact release candidate, current Apple policy, metadata, screenshots, privacy/payment evidence and reviewer journeys. Its [Capacitor release-integrity contract](https://github.com/CodeAlive-AI/vibe-stack/blob/main/skills/apple-app-store-reviewer/references/capacitor-release-integrity.md) adds source/generated/submitted parity checks beyond this skill's engineering checks. It does not cover Google Play review.

Pass the commit and build identity, resolved dependency inventory, web/native asset hashes, final archive when available, and test reports with missing evidence clearly marked. Do not pass credentials or claim that this skill's static checks establish submission readiness. If the audit finds implementation defects, return the finding IDs, evidence and acceptance checks to `agentic-capacitor` for authorized fixes, then review the new release candidate; previous evidence may no longer apply.

Use an available installed companion by name or consult its canonical source above under the normal access policy. Neither skill requires installing the other. Missing companion access must be disclosed without weakening the evidence requirements. Cross-references do not authorize installation, automatic mutual invocation, app changes or uploads.
