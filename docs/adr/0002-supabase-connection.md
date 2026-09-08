# 0002: Supabase connection

## Status
Accepted

## Context
While deploying on Render, connecting to the Supabase database
failed with "Network is unreachable". Cause: Supabase's direct
database connection is IPv6-only, and Render does not support
outbound IPv6 — the two are incompatible without an intermediary.

## Decision
Use Supabase's Connection Pooler instead of the direct
connection string. The pooler supports both IPv4 and IPv6, acting
as a compatible intermediary between Render and Supabase.

## Alternatives
- Supabase IPv4 add-on ($4/month): rejected

## Consequences
Slightly higher latency due to the additional routing layer, but
required for Render/Supabase compatibility.