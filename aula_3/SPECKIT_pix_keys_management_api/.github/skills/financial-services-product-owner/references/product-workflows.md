# Product Workflows

Use this file when the request needs a deeper workflow than the main `SKILL.md`.

## Discovery And Problem Framing

Use for ambiguous asks, new opportunities, weakly defined pain points, or requests to "shape" a feature.

Checklist:

- Identify the user, trigger event, and current workaround.
- Clarify the business problem and why it matters now.
- Separate symptom from root cause.
- Define the baseline metric and target outcome.
- Capture domain constraints: money movement, identity, reporting, servicing, or partner obligations.
- Note what happens if nothing changes.

Good outputs:

- problem statement
- opportunity assessment
- discovery plan
- hypothesis list

## Delivery Specification

Use for requests to write requirements, stories, acceptance criteria, or engineering-ready scope.

Checklist:

- Define the business flow end to end.
- Mark in-scope and out-of-scope steps.
- Identify upstream systems, downstream systems, and manual operations.
- Write acceptance criteria that are observable and testable.
- Include exception paths, retries, reversals, and failure handling when relevant.
- Specify required logging, auditability, and reporting behaviors.

Good outputs:

- feature brief
- PRD section
- epic with stories
- acceptance criteria table

## Prioritization

Use for roadmap tradeoffs, backlog ranking, or release scope decisions.

Scoring dimensions:

- customer value
- revenue or retention impact
- risk reduction or control improvement
- compliance or audit urgency
- operational efficiency
- effort and dependency load
- reversibility

Recommended output:

| Option | Value | Risk Reduction | Effort | Urgency | Recommendation |
| --- | --- | --- | --- | --- | --- |

Explain why the top choice wins and what is deferred.

## Launch And Change Management

Use for launch planning, rollout design, training, or operational readiness.

Checklist:

- Define rollout cohort and guardrails.
- Confirm monitoring, alerts, and dashboards.
- Confirm support, operations, finance, and compliance readiness.
- Plan user communication and internal enablement.
- Define rollback, pause, or kill-switch conditions.
- Decide post-launch review window and success thresholds.

Good outputs:

- launch checklist
- readiness memo
- phased rollout plan

## Incident And Control Follow-Up

Use after outages, processing failures, audit findings, reconciliation breaks, or repeat support issues.

Checklist:

- Describe the customer and operational impact.
- Distinguish immediate containment from durable fix.
- Identify which control failed, was missing, or was bypassed.
- Translate root cause into backlog actions.
- Define ownership across product, engineering, and operations.
- Add prevention metrics and review cadence.

Good outputs:

- corrective action plan
- control improvement backlog
- post-incident product recommendations
