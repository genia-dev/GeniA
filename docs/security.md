# Security

GeniA is stateless. It connects with cloud DBs for conversation storage and handles secrets via environment variables. Plans are in place for standard secrets store provider integration.

On the subject of secrets management, the project currently utilizes environment variables, as defined in the [.env.template](https://github.com/genia-dev/GeniA/blob/main/.env.template) file. However, we are actively developing integrations with standard secrets store providers for improved security.

**We presently advise the integration of GeniA within a designated private channel, accessible exclusively to a whitelist of approved engineers.**

We are actively developing Single Sign-On (SSO) and Role-Based Access Control (RBAC) features for GeniA. These enhancements are slated for release in the near future.