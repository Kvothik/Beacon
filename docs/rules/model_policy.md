# Model Policy

## Purpose

This document defines the intended low-cost model policy for Beacon autonomous execution.

## Default Model Roles

- Sixx -> cheapest safe coordinator model
- Sentinel -> cheapest safe watchdog / QA model
- Forge -> cheapest safe coding-capable default model
- Atlas -> cheapest safe coding-capable default model

## Escalation Policy

Use a stronger model only when:
- the issue is high complexity
- the issue is blocked on reasoning/debugging quality
- the default coding model failed once on a legitimate hard problem

Escalation should be temporary, not permanent.

## Cost Rules

- Sixx must not stay on an expensive coding model for long-running coordination
- queue tracking, board sync, and status updates must stay on cheap models
- worker default models should be cheaper than top-tier reasoning models when possible
- stronger models should be used only for implementation turns that actually need them

## Fallback Rule

If the preferred model is unavailable:
- use the cheapest working safe fallback
- do not silently pin all agents to the most expensive working model
- record the fallback choice clearly

## Verification

When model policy changes, report:
- active model by agent
- default model by agent
- escalation model by agent
- known unavailable preferred models