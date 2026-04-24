# Finserv Risk Checklist

Use this file when the request touches regulated workflows, operational controls, or sensitive customer outcomes.

## Regulatory And Policy Scope

- Which product, entity, and geography are in scope?
- Does the change affect disclosures, pricing, suitability, consent, or reporting?
- Is legal or compliance sign-off likely required?
- Are there existing internal policies or audit findings that constrain the design?

## Funds And Transaction Integrity

- Does this change create, modify, route, settle, reverse, or report financial transactions?
- Could it affect balances, statements, reconciliation, or fee calculation?
- What controls prevent duplicate, missing, or out-of-order processing?
- What is the fallback if an external processor or ledger step fails?

## Identity, Access, And Fraud

- Does the flow create or weaken identity proofing, authentication, or authorization controls?
- Could it increase fraud vectors such as account takeover, synthetic identity, or abuse of refunds or promotions?
- Are suspicious actions observable and reviewable?

## Data, Privacy, And Security

- What customer or transaction data is collected, exposed, retained, or shared?
- Does the design minimize access to sensitive data?
- Are logging and analytics safe from leaking restricted values?
- Are there third-party data transfers or storage concerns?

## Operational Controls

- Which team owns exceptions?
- Is there a reconciliation or daily control process?
- Are approvals, overrides, and manual adjustments tracked?
- Can support and operations understand the state of a transaction or case?

## Vendor And Dependency Risk

- Which vendors, processors, or internal platforms are critical?
- What happens on timeout, partial success, duplicate callbacks, or stale data?
- Are rate limits, SLAs, and cut-off times relevant?

## Release Risk

- Is phased rollout possible?
- Are there feature flags, cohort limits, or transaction caps?
- What metrics indicate safe continuation versus rollback?

## Minimum Output Expectation

When this checklist is relevant, the answer should explicitly name:

- the main risk categories in play
- the highest-risk failure mode
- the control or mitigation expected
- the owner or team that must be involved
