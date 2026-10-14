# Free compute

Your own computer only needs a browser. Everything runs in the cloud.

Free tiers change often, and several numbers below come from third-party write-ups,
not the providers. They were checked in October 2026. **Confirm on the provider's
own page before you rely on one.**

| Use it for | Service | Free allowance | Catches |
|---|---|---|---|
| **Daily coding, the fake server, a small model on CPU** (Phase 1) | GitHub Codespaces | 120 core-hours a month on a personal Free plan, so about 60 hours on the default 2-core machine, plus 15 GB of storage | Stop the Codespace when you finish. Storage counts even while it's stopped, so delete old ones. |
| **GPU measurements** (end of Phase 1, Phase 5) | Kaggle Notebooks | About 30 GPU-hours a week on a T4 or P100. Kaggle doesn't publish a fixed number; your account settings show yours. Sessions last up to about 12 hours. | GPU and internet access need phone verification. |
| Backup GPU | Google Colab (free) | A T4 when one is free | Not guaranteed at busy times. Idle sessions disconnect. |
| **Several machines** (Phases 2–4) | Start with `kind`, which runs Kubernetes "machines" as containers inside one Codespace | Free; it uses your Codespace hours | All the "machines" share one box, so it's good for learning behavior, not for speed. |
| Real separate VMs, later | Oracle Cloud Always Free (Arm) | Reportedly cut in mid-2026 from 4 CPUs and 24 GB to **2 CPUs and 12 GB** in total | Needs a card. Arm CPUs. Popular regions can run out of capacity. |
| Short GPU jobs (Phase 5) | Modal Starter plan | Reportedly $30 of compute credit a month | Set a spending limit first. |

**Hold off on** the Google Cloud $300 trial and AWS credits for now. They expire,
GPUs need quota requests, and a forgotten machine bills real money. If you ever
add a card anywhere, set a budget alert before you start anything.

## What about the Claude Code cloud session?

It can run the tests, the fake server, and the load generator. Its network policy
currently blocks `huggingface.co`, so it can't download models. To allow it, edit
the environment's **Network access** setting and add that domain
(see https://code.claude.com/docs/en/cloud-environments#network-access).
Codespaces is simpler for running models.

## Sources

- [GitHub Codespaces billing (GitHub Docs)](https://docs.github.com/pt/billing/managing-billing-for-your-products/managing-billing-for-github-codespaces)
- [Free cloud GPUs in 2026 (gpuperhour.com)](https://gpuperhour.com/blog/free-cloud-gpus-and-credits)
- [Kaggle's updated notebook resources](https://lilys.ai/en/notes/google-tpu-20251128/free-kaggle-gpu-29gb-4-cpu-update)
- [Google Colab GPU limits (Hivenet)](https://www.hivenet.com/post/google-colaboratory-gpu-complete-guide-to-free-cloud-gpu-access-and-limitations)
- [Oracle Cloud free tier limits (InfoQ)](https://infoq.com/news/2026/07/oracle-cloud-free-tier-limits/)
- [Oracle Cloud free tier changes 2026 (TerminalBytes)](https://terminalbytes.com/oracle-cloud-free-tier-changes-2026)
- [Modal free plan (CostBench)](https://www.costbench.com/software/ai-gpu-cloud/modal/free-plan/)
- [Modal pricing (Morph)](https://www.morphllm.com/modal-pricing)
