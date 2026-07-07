# Security Practices

Security defaults should keep the MVP fast, but not casual. The goal is a small baseline that is easy for agents to apply, verify, and maintain.

## Default Rule

Use product-owned authentication for product users, and use infrastructure access control for infrastructure surfaces.

| Need | Default |
| --- | --- |
| Product users and product admin | [Better Auth](https://www.better-auth.com/) |
| Infrastructure SSO/MFA gateway | [Authelia](https://www.authelia.com/) |

## Better Auth

Use Better Auth for the application itself:

- user sign-in and sessions;
- product roles and permissions;
- product admin dashboards;
- billing, organizations, support, and user workflows;
- auth logic that must be visible in the application code and database.

Better Auth stays the default for TypeScript web apps because it lives inside the product and works well with the Vibe Stack web defaults.

## Authelia

Use Authelia when the product or infrastructure needs a lightweight, reliable, self-hosted authentication gateway with multi-user auth, MFA, and passkeys.

Good fits:

- server admin surfaces;
- internal tools and dashboards;
- staging environments;
- agent services such as OpenClaw or Hermes Agent;
- self-hosted apps that should sit behind SSO/MFA;
- services that need protection before traffic reaches the app.

Authelia is not a replacement for product authorization. Treat it as an access layer in front of applications, servers, and agent runtimes when centralized SSO/MFA is the simpler and safer default.

## Agent Rules

- Keep auth decisions explicit: product auth and infrastructure auth are different concerns.
- Do not add an external identity layer when simple in-app auth is enough.
- Do not rely on network hiding alone for admin or agent surfaces.
- Fail closed when auth configuration is missing or invalid.
- Prefer clear access errors over silent bypasses or permissive fallbacks.

Sources: [Better Auth](https://www.better-auth.com/), [Authelia](https://www.authelia.com/), [Authelia proxy integrations](https://www.authelia.com/integration/proxies/introduction/), [Authelia OpenID Connect provider](https://www.authelia.com/configuration/identity-providers/openid-connect/provider/).
