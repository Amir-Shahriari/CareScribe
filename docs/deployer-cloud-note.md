# Deployer note — the optional cloud generation path

Cloud generation is **off**. This note explains what turning it on would mean.
If you do not need it, skip this file; the app is complete without it.

## What it changes, and what it does not

De-identification, review, approval, and re-identification stay entirely on the
clinician's machine in every configuration. Cloud generation changes exactly one
thing: where the drafting model runs.

What the provider would receive is what the local model receives today — the
**approved de-identified text**, placeholders only, after the reviewer approved
it and the residual sweep came back clean. It never receives the identity
mapping, the original document, or a re-identified draft. There is no code path
by which it could: the mapping is not a parameter to any backend, and
`carenotes.assert_deidentified()` raises rather than sending if a mapping value
is present in the outgoing prompt.

**This does not make it a good idea by default.** De-identified clinical text is
still clinical text, still potentially re-identifiable in combination with other
data, and sending it off-premises is a decision for your information governance
process, not an application default.

## Enabling it

Two separate environment variables are required:

```
CARESCRIBE_CLOUD_PROVIDER=anthropic | openai
CARESCRIBE_CLOUD_API_KEY=<key>
```

Two more are optional:

```
CARESCRIBE_CLOUD_BASE_URL=<https://your-endpoint>   # override the API root
CARESCRIBE_CLOUD_MODEL=<model-name>                 # required for openai
```

Two required switches on purpose. A key left in the environment by an unrelated
tool must not silently enable off-device generation, and naming a provider
without a key fails loudly rather than quietly falling back to something local.

`CARESCRIBE_CLOUD_PROVIDER` selects the wire format:

- **`anthropic`** — the Messages API. Defaults to `https://api.anthropic.com`
  and model `claude-opus-5`; override either with the optional variables.
- **`openai`** — the OpenAI Chat Completions shape, which **Azure OpenAI, a
  private gateway, vLLM, and most self-hosted servers also speak**. This is the
  path for "our own API endpoint". Set `CARESCRIBE_CLOUD_BASE_URL` to your
  endpoint and `CARESCRIBE_CLOUD_MODEL` to the model name it expects (there is
  no sensible default for a private endpoint, so the model is mandatory here).

The transport is standard-library HTTP only — no provider SDK is a dependency,
so "this app ships no third-party network client" stays checkable. No key is
ever bundled, defaulted, written to disk, or logged. It is read from the
environment at call time. Tests assert `core/backends.py` and
`core/cloud_client.py` contain no key-shaped literal and never store one on an
instance.

Even fully configured, cloud is **last** in the selection order: a local Ollama
daemon wins, then the built-in model, then cloud. It is a fallback, not a
preference.

## Before you enable it

- **A paid, no-training tier.** The provider must contractually not train on
  submitted content, and not retain it beyond what is needed to serve the
  request. A consumer or free tier is not acceptable.
- **A data processing agreement** covering the provider as a processor, and — in
  the UK — confirmation of where the data is processed.
- **Information governance sign-off**, recorded, naming the provider and the
  tier. The same review you would run for any other processor.
- **Tell the clinician.** The app's privacy indicator changes automatically when
  cloud is configured: it stops saying "running fully offline" and names the
  provider. Do not remove or reword that.

## The transport

`core/cloud_client.py` implements streaming against both wire formats above.
`CloudBackend` still validates configuration at construction and is still last
in the selection ladder and off unless both required variables are set — wiring
the transport does not change any of that. It changes one thing: a fully
configured, IG-signed-off deployment now generates instead of raising.

What the model receives is unchanged from every other backend: approved
de-identified text with placeholders, after `carenotes.assert_deidentified()`
has run. The identity mapping is not a parameter to `CloudBackend` and there is
no code path from it to the transport.
