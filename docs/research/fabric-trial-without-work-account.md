# Fabric trial without a work or school account

Researched 2026-11-25. The question: how can someone who has only a personal email (Gmail, Outlook.com) and no work or school account use a Microsoft Fabric trial? Facts come from Microsoft Learn, Microsoft pricing and offer pages, and the Azure Retail Prices API. Anything else is labelled **community/opinion**. Anything not confirmed is marked **unverified**.

## Summary

| Option | Works with personal email? | Cost | Time limit | Source |
|---|---|---|---|---|
| Sign in to Fabric directly with Gmail/Outlook.com | **No.** A work or school account is required | - | - | [Sign up as an individual](https://learn.microsoft.com/en-us/power-bi/fundamentals/service-self-service-signup-purchase-for-power-bi) |
| Azure free account, then a new Entra user `name@<tenant>.onmicrosoft.com`, then the Fabric trial | **Yes.** This is the route Microsoft documents | Free. A card and phone are needed for verification | Fabric trial: 60 days. Azure credit: $200 for 30 days | [Fabric trial with a personal email](https://learn.microsoft.com/en-us/fabric/fundamentals/free-trial-account-personal-email), [Azure free account](https://azure.microsoft.com/en-us/pricing/purchase-options/azure-account) |
| Microsoft 365 business trial (for example Business Premium), then the Fabric trial | Yes. The trial creates an `onmicrosoft.com` work account | Free for 1 month. A credit card is needed, and the trial **renews to paid** unless you turn off recurring billing | 30 days | [Sign up as an individual](https://learn.microsoft.com/en-us/power-bi/fundamentals/service-self-service-signup-purchase-for-power-bi), [Try or buy Microsoft 365](https://learn.microsoft.com/en-us/microsoft-365/commerce/try-or-buy-microsoft-365) |
| Microsoft 365 Developer Program E5 sandbox | **Not for most individuals.** You can join with a personal Microsoft account, but a sandbox needs Visual Studio Pro/Enterprise, a partner programme, or Premier/Unified Support | Free, but a billing account must be linked | Up to 90 days | [Developer Program FAQ](https://learn.microsoft.com/en-us/office/developer-program/microsoft-365-developer-program-faq) |
| Pay for an F2 capacity in Azure | Yes, through the same Azure account and Entra user as option 2 | $0.36 per hour in East US (2 CU × $0.18), billed per second, $0 compute while paused | None | [Azure Retail Prices API](https://prices.azure.com/api/retail/prices?$filter=serviceName%20eq%20'Microsoft%20Fabric'%20and%20armRegionName%20eq%20'eastus'), [Licenses](https://learn.microsoft.com/en-us/fabric/enterprise/licenses), [Pause and resume](https://learn.microsoft.com/en-us/fabric/enterprise/pause-resume) |

**Recommendation for this repo's getting started guide:** use option 2. It is the only route Microsoft documents specifically for Fabric with a personal email. It costs nothing if you stay on the free Azure offer, and it gives you a tenant where you are the top admin.

## 1. Can a personal email start a Fabric trial directly?

No.

- Power BI/Fabric sign-up says: "To sign up for the Power BI service, you need a work or school email account. You can't use consumer email accounts (for example, Gmail or Hotmail) directly." One of the listed reasons for not seeing a trial is "You're using a personal or consumer email account without first creating a Microsoft 365 trial account." ([Sign up or purchase Power BI as an individual](https://learn.microsoft.com/en-us/power-bi/fundamentals/service-self-service-signup-purchase-for-power-bi), ms.date 2026-03-23)
- The main Fabric trial page does not mention personal email at all. It says only that "Trial eligibility depends on factors such as your tenant settings, license state, and the number of trial capacities available in your tenant" ([Fabric trial capacity](https://learn.microsoft.com/en-us/fabric/fundamentals/fabric-trial), ms.date 2026-08-12).
- Microsoft does publish a page for this exact case: "If you don't have access to a work account, you can still start a Microsoft Fabric free trial by using a personal email address." It does not sign you in with the personal email. Instead you create a work-style user in a new Entra tenant (section 2) ([Start a Fabric free trial with a personal email](https://learn.microsoft.com/en-us/fabric/fundamentals/free-trial-account-personal-email), ms.date 2026-02-27).

## 2. The documented route: Azure free account → Entra user → Fabric trial

### Microsoft's steps

From [Start a Fabric free trial with a personal email](https://learn.microsoft.com/en-us/fabric/fundamentals/free-trial-account-personal-email):

- **Prerequisites:** "A personal email address (for example, Outlook, Gmail, or Yahoo)", "A phone number and payment method for Azure account verification, if prompted", and the Microsoft Authenticator app ("optional but recommended").
- **Create an Azure trial account:** go to the Azure free account page, select **Try Azure for free**, then sign in or **Sign up** with your personal email. "You may be asked to verify your identity with a phone number and provide a payment method ... you won't be charged unless you explicitly upgrade to a paid subscription."
- **Create a user in Microsoft Entra ID:** in the Azure portal open **Microsoft Entra ID** > **Manage** > **Users** > **New user** > **Create new user**. Set a password. "You don't have to set role assignments or other properties." Copy the user principal name (UPN).
- **Sign in to Fabric** at `app.fabric.microsoft.com` with that UPN and password, and set up two-factor authentication when prompted.
- **Activate the trial:** profile icon > **Free trial** > choose a capacity region > **Activate**.

### Requirements, in detail

- **Azure free account terms:** a $200 credit "to use on Azure services within 30 days", 12 months of free amounts for popular services, and 65+ always-free services. You need a phone number, a non-prepaid credit or debit card, and a Microsoft or GitHub account. A temporary $1 authorisation hold is placed and then reversed. "We'll never charge you unless you decide to move to pay-as-you-go pricing." New customers only, one free account per customer ([Azure free account](https://azure.microsoft.com/en-us/pricing/purchase-options/azure-account)).
- **Tenant and domain:** "If you don't already have a tenant, one is created automatically when you acquire a free, trial, or paid Microsoft online service license" ([Licenses](https://learn.microsoft.com/en-us/fabric/enterprise/licenses)). New tenants get an `<name>.onmicrosoft.com` domain, and "the user who creates a Microsoft Entra tenant is automatically assigned the Global Administrator role" ([Create a new tenant](https://learn.microsoft.com/en-us/entra/fundamentals/create-new-tenant), ms.date 2026-07-29).
- **Why a new user is needed:** this is **unverified** in the Fabric docs, which never explain it. The likely reason is that your personal Microsoft account sits in the new tenant as an outside account, and Fabric needs a work or school identity. Related: "B2B users can't be capacity administrators" ([Buy Fabric capacity](https://learn.microsoft.com/en-us/fabric/enterprise/buy-capacity)).
- **Per-user licence:** none to buy. "A Free (Fabric) license is automatically assigned the first time a user signs in to the Fabric portal (if the tenant has Fabric enabled)" ([Licenses](https://learn.microsoft.com/en-us/fabric/enterprise/licenses)). Starting the capacity trial also gives "a complementary Power BI individual trial (if you didn't already have a Power BI *paid* license)", which works like Premium Per User ([Fabric trial](https://learn.microsoft.com/en-us/fabric/fundamentals/fabric-trial)).
- **Tenant settings:**
  - "**Users can try Fabric paid features** is enabled by default. ... Changing [it] from enabled to disabled blocks self-service trials of new licenses and of the Fabric capacity trial." ([Help and support settings](https://learn.microsoft.com/en-us/fabric/admin/service-admin-portal-help-support), ms.date 2026-04-08)
  - **Users can create Fabric items** must be on. Changing it requires the *Fabric administrator* Entra role ([Enable Fabric](https://learn.microsoft.com/en-us/fabric/admin/fabric-switch)). Its default state for a brand-new tenant is not stated on that page (**unverified**).
  - The Fabric trial page lists both settings as the way to enable trials. It notes: "The previous option **Enabled for the entire organization** in the **Trial** section is no longer available." ([Fabric trial](https://learn.microsoft.com/en-us/fabric/fundamentals/fabric-trial))
- **Power BI self-service sign-up:** the Power BI page says sign-up can be blocked if the "Microsoft 365 Billing administrator disabled self-service options" ([Sign up as an individual](https://learn.microsoft.com/en-us/power-bi/fundamentals/service-self-service-signup-purchase-for-power-bi)). In a tenant you created yourself, you control these settings. Whether self-service is on by default in an Azure-created tenant is **unverified**.
- **Who is admin:**
  - The person who starts the trial "becomes the Capacity administrator for that trial capacity" ([Fabric trial](https://learn.microsoft.com/en-us/fabric/fundamentals/fabric-trial)).
  - The Fabric admin portal is for the **Fabric administrator** or **Power Platform administrator** roles. **Global administrator** has "Unlimited access to all management features" and can assign roles ([Admin roles](https://learn.microsoft.com/en-us/fabric/admin/roles)).
  - The new Entra user has no role by default. If you need to change tenant settings, use the Global Administrator account (the one that created the tenant) to give that user the Fabric administrator role. This is an inference from the pages above; no Microsoft page states this step for this scenario.
- **What the trial gives you:** 60 days on an F4 or F64 capacity, up to 1 TB of OneLake storage, and all workloads. Copilot, AI functions, data agents and Private Link are not included. When the trial ends, non-Power BI items go inactive, and "All content remains stored in OneLake for 7 days" ([Fabric trial](https://learn.microsoft.com/en-us/fabric/fundamentals/fabric-trial)).
- **No guaranteed second trial:** "Eligibility for another trial isn't guaranteed, and Microsoft might restrict repeated or successive trial usage" ([Fabric trial](https://learn.microsoft.com/en-us/fabric/fundamentals/fabric-trial)).

## 3. Other official options

### Microsoft 365 business trial

- Power BI's own advice for people without a work email: "Sign up for a Microsoft 365 trial to create a work email account (*onmicrosoft.com*) and a new tenant. The Microsoft 365 trial includes up to 25 licenses and you become the admin for the new tenant. You need a credit card to sign up, so be sure to cancel the trial before 30 days if you aren't ready to purchase." It adds: "Microsoft 365 Business Premium trials include Power BI Pro and are widely available." ([Sign up as an individual](https://learn.microsoft.com/en-us/power-bi/fundamentals/service-self-service-signup-purchase-for-power-bi))
- The trial lasts one month ("Try free for 1 month"). "Trial-only tenants are limited to 30 days and 300 GB." "At the end of your trial period, your subscription renews to an annual term subscription by default, unless you turn off **recurring billing**" ([Try or buy Microsoft 365](https://learn.microsoft.com/en-us/microsoft-365/commerce/try-or-buy-microsoft-365), ms.date 2026-04-23).
- **Watch out:** the tenant is useful for only 30 days, but the Fabric trial runs for 60. Fabric itself has no stated dependency on the Microsoft 365 subscription. What happens to the tenant and the Fabric trial after the Microsoft 365 trial lapses is **unverified**.
- The Microsoft 365 product page ([Business Premium](https://www.microsoft.com/en-us/microsoft-365/business/microsoft-365-business-premium)) timed out twice, so the current price after the trial was not checked (**unverified**).

### Microsoft 365 Developer Program

From the [Developer Program FAQ](https://learn.microsoft.com/en-us/office/developer-program/microsoft-365-developer-program-faq) (ms.date 2026-09-04):

- **Joining:** you can join with a personal Microsoft account. However, "Phone numbers and email accounts with the *.onmicrosoft.com domain are not supported."
- **Who gets a sandbox:** only "qualifying program members":
  1. people with an eligible Visual Studio Professional or Enterprise subscription;
  2. companies in the ISV Success Program or eligible Microsoft AI Cloud Partner Program tiers;
  3. Premier or Unified Support customers.

  Microsoft employees are excluded. Anyone with only a personal email and none of these does **not** qualify.
- **What a sandbox includes:** a Microsoft 365 E5 developer subscription with 25 licences, which "includes a Power BI Pro license. It does not include Power BI Premium." The FAQ does not mention Fabric.
- **How long it lasts:** "good for up to 90 days". "Microsoft may require tenants to be recreated every 90 days."
- **Billing:** "Linking a valid billing account is mandatory during sandbox setup and can't be bypassed." The sandbox itself stays free.

### Paying for an F2 capacity in Azure

- **Price:**
  - The Azure Retail Prices API lists "Compute Pool Capacity Usage CU" in East US at **$0.18 per CU-hour** (pay-as-you-go, effective 2023-11-01). An F2 is 2 CU, so it costs **$0.36 per hour**, about $263 for a full 730-hour month ([Retail Prices API query](https://prices.azure.com/api/retail/prices?$filter=serviceName%20eq%20'Microsoft%20Fabric'%20and%20armRegionName%20eq%20'eastus'), [API docs](https://learn.microsoft.com/en-us/rest/api/cost-management/retail-prices/azure-retail-prices)). The monthly figure is my arithmetic.
  - OneLake hot storage is $0.026 per GB per month (same API).
  - The public [Fabric pricing page](https://azure.microsoft.com/en-us/pricing/details/microsoft-fabric/) loads its prices with scripts and showed "$-" when fetched, so the figures come from the API instead.
- **Billing model:** "Azure bills you per second with no commitment ... Pricing is regional, and Azure bills per second with a one-minute minimum" ([Licenses](https://learn.microsoft.com/en-us/fabric/enterprise/licenses)).
- **Pause and resume:**
  - You pause and resume in the Azure portal or through the REST API, and can schedule it with an Azure runbook. "Resuming your capacity also resumes billing."
  - When you pause, "the remaining cumulative overages and smoothed operations on your capacity are summed, and added to your Azure bill" ([Pause and resume](https://learn.microsoft.com/en-us/fabric/enterprise/pause-resume), ms.date 2026-04-20).
  - The pricing page FAQ says OneLake storage is still billed while the capacity is paused ([Fabric pricing](https://azure.microsoft.com/en-us/pricing/details/microsoft-fabric/)).
- **Prerequisites to buy:**
  - a Fabric free or Power BI licence;
  - an Azure subscription in the same tenant;
  - the `Microsoft.Fabric` resource provider registered;
  - enough CU quota in that region.

  The capacity admin "must belong to the tenant" and cannot be a B2B user ([Buy Fabric capacity](https://learn.microsoft.com/en-us/fabric/enterprise/buy-capacity), ms.date 2026-11-19).
- **Quota:** "Quotas depend on your Azure subscription type" ([Fabric quotas](https://learn.microsoft.com/en-us/fabric/enterprise/fabric-quotas), ms.date 2026-11-20). Whether a *free-account* Azure subscription has any Fabric CU quota is not stated (**unverified**). You may need to upgrade to pay-as-you-go or request quota.
- **Do you still need Power BI Pro?**
  - Not for Fabric items. A Free licence lets you "create and share non-Power BI Fabric items when the workspace runs on a Fabric (F) or Trial capacity".
  - Yes for Power BI items. "On F SKUs smaller than F64, each user viewing Power BI content must have Pro, PPU, or an individual trial", and "To create Power BI items in a workspace other than *My workspace* ... you need a Power BI Pro or ... PPU license, or a Power BI individual trial" ([Licenses](https://learn.microsoft.com/en-us/fabric/enterprise/licenses)).
  - So on F2, lakehouses, notebooks and pipelines work with a Free licence, but semantic models and reports outside My workspace need Pro.
- **Cost trap: capacity overage.** "Capacity overage is enabled by default when you create a Fabric capacity". It bills excess usage "at three times the pay-as-you-go rate", and its threshold "isn't a hard spending cap" ([Capacity overage](https://learn.microsoft.com/en-us/fabric/enterprise/capacity-overage-overview), ms.date 2026-08-26). Turn it off when you create a learning capacity.

## 4. Recent changes (2025–2026)

Dates are the page `ms.date` values unless stated otherwise. Microsoft does not always say when the underlying change happened.

- **2026-02-27:** Microsoft Learn page [Start a Fabric free trial with a personal email](https://learn.microsoft.com/en-us/fabric/fundamentals/free-trial-account-personal-email) (ms.date; last updated 2026-04-08). This is the first official Fabric page for this scenario that I found; the exact publish date is **unverified**.
- **2026-03-23:** the Power BI sign-up page now has a "Don't have a work or school email?" row pointing to a Microsoft 365 trial, and names Business Premium as the widely available trial that includes Pro ([Sign up as an individual](https://learn.microsoft.com/en-us/power-bi/fundamentals/service-self-service-signup-purchase-for-power-bi)).
- **By 2026-07-29:** "Only paid customers can create a new Workforce tenant in Microsoft Entra ID. Customers using a free tenant, or a trial subscription won't be able to create additional tenants". People in that position are pointed to the Azure free account ([Create a new tenant](https://learn.microsoft.com/en-us/entra/fundamentals/create-new-tenant)).
- **July 2026:** new Developer Program sandboxes are "instant sandboxes", some with add-on purchasing. Setup needs a linked billing account ([Developer Program FAQ](https://learn.microsoft.com/en-us/office/developer-program/microsoft-365-developer-program-faq)).
- **By 2026-08-12:** the Fabric trial is now "either an F4 ... or an F64 capacity", with a **Change size** button to move between 4 and 64 CU "if eligible". The old trial option "Enabled for the entire organization" was replaced by tenant settings ([Fabric trial](https://learn.microsoft.com/en-us/fabric/fundamentals/fabric-trial)).
- **By 2026-08-26:** capacity overage exists, and it is on by default for new F capacities ([Capacity overage](https://learn.microsoft.com/en-us/fabric/enterprise/capacity-overage-overview)).
- **2026-11-19 / 20:** the buy-capacity and quota pages now include overage thresholds in the quota you need ([Buy Fabric capacity](https://learn.microsoft.com/en-us/fabric/enterprise/buy-capacity), [Fabric quotas](https://learn.microsoft.com/en-us/fabric/enterprise/fabric-quotas)).

## Conflicts and unclear points

- **Trial size:**
  - The trial page says F4 *or* F64.
  - The licenses page still lists "Trial | 64" and says "Free trial includes F64 capacity equivalent" ([Licenses](https://learn.microsoft.com/en-us/fabric/enterprise/licenses)).
  - The Premium page footnote agrees with F4 or F64 ([What is Power BI Premium](https://learn.microsoft.com/en-us/fabric/enterprise/powerbi/service-premium-what-is)).
  - Who gets F4 and who gets F64 is not explained.
- **Two different "official" routes:**
  - The Fabric docs use an **Azure free account**.
  - The Power BI docs use a **Microsoft 365 trial**.
  - Neither page mentions the other.
  - The Azure route is better for a 60-day Fabric trial, because the Microsoft 365 trial tenant is limited to 30 days and renews to paid by default.
- **Personal email wording:** the Fabric page says to "create a user with your personal email address" in Entra. Entra users get an `@<tenant>.onmicrosoft.com` UPN, and the page itself says to sign in with the UPN. The wording probably means the personal address as a contact email, but this is **unclear**.
- **Capacity overage wording:** the overage page calls it "an opt-in feature" and also says it "is enabled by default when you create a Fabric capacity".
- **Payment method:** the Fabric page says a card is needed "if prompted". The Azure offer page lists a non-prepaid card as required.

## Common in practice (community/opinion)

These are not Microsoft guidance.

- Microsoft Q&A threads ([example 1](https://learn.microsoft.com/en-us/answers/questions/2114450/do-i-need-a-corporate-email-to-open-free-trial-fab), [example 2](https://learn.microsoft.com/en-us/answers/questions/5911904/how-to-get-access-to-ms-fabric-if-i-dont-have-a-co)) and Fabric community forum posts repeat the same two workarounds: an Azure free account plus a new Entra user, or a Microsoft 365 trial. They were seen in search snippets only (**unverified** wording).
- Forum posts report that school accounts are sometimes blocked from trials by the school's tenant settings ([Fabric community](https://community.fabric.microsoft.com/t5/Fabric-platform/Fabric-Trial-blocked-on-school-account-any-workaround/td-p/4705962), search snippet only).

## Unverified

- Default state of **Users can create Fabric items** and of Power BI self-service sign-up in a tenant created by an Azure free account.
- Whether an Azure free-account subscription has Fabric CU quota for an F2.
- Why Fabric needs a new Entra member user instead of the personal Microsoft account that created the tenant.
- What happens to a Fabric trial in a Microsoft 365 trial tenant after the Microsoft 365 trial ends at 30 days.
- Current Microsoft 365 Business Premium price after the trial (the product page timed out).
