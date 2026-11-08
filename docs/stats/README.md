# Weekly summaries

Every Monday, `.github/workflows/weekly-stats.yml` runs `tools/weekly_stats.py`, which writes
`<date>.md` here (and posts it as an issue labeled "weekly summary"), and keeps
`snapshot.json` to compare the next week with. Nothing is collected inside the apps.

## Connecting Cloudflare (website visitors)

The "Website visitors" section reads Cloudflare Web Analytics. It needs a Cloudflare API token,
saved in GitHub as a secret (the summary runs on GitHub's servers):

1. Cloudflare: My Profile > API Tokens > Create Token > **Create Custom Token**.
   - Name: `GitHub weekly summary (read-only)`
   - Permissions: **Account > Account Analytics > Read** (only that).
   - Account Resources: Include > your account.
   - Continue to summary > Create Token, and copy it (it's shown once).
2. GitHub: Kanzonas-Site > **Settings > Secrets and variables > Actions > New repository
   secret**. Name: `CF_ANALYTICS_TOKEN`, Secret: the token. Add secret.
3. To try it: Actions > Weekly summary > Run workflow. The new issue's "Website visitors"
   section shows the visits since the last summary.

Without the secret, that section says "Not connected yet"; with a token that lacks the
permission, it says what Cloudflare answered. The rest of the summary works either way.
