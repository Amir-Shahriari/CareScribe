import {
  ShieldCheck,
  ArrowUpRight,
  ArrowRight,
  WifiOff,
  FileCheck,
  KeyRound,
  Trash2,
} from "lucide-react";

const REPO = "https://github.com/Amir-Shahriari/CareScribe";

function Wordmark({ className = "" }: { className?: string }) {
  return (
    <span className={`inline-flex items-center gap-2 font-semibold tracking-tight ${className}`}>
      <ShieldCheck className="h-[18px] w-[18px] text-accent" strokeWidth={2} aria-hidden />
      CareScribe
    </span>
  );
}

function Nav() {
  return (
    <header className="sticky top-0 z-30 border-b border-line/80 bg-bg/80 backdrop-blur-sm">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-5 sm:px-8">
        <a href="#top" className="text-[15px] text-ink">
          <Wordmark />
        </a>
        <nav className="flex items-center gap-5 text-[13.5px] font-medium text-muted sm:gap-7">
          <a href="#how" className="transition-colors hover:text-ink">
            How it works
          </a>
          <a
            href={REPO}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1 transition-colors hover:text-ink"
          >
            GitHub
            <ArrowUpRight className="h-4 w-4" strokeWidth={2} aria-hidden />
          </a>
        </nav>
      </div>
    </header>
  );
}

/*
 * Illustrative representation of the de-identification step: real CareScribe
 * placeholder tokens over fabricated referral text. Not a product screenshot.
 * Swap this component for a real screenshot of the app when one is available.
 */
function RedactionVisual() {
  return (
    <figure className="rise rise-3 w-full">
      <div className="overflow-hidden rounded-2xl border border-border bg-surface shadow-cs">
        <div className="grid divide-y divide-line">
          <div className="p-5">
            <p className="mb-3 text-[11px] font-semibold uppercase tracking-[0.14em] text-muted">
              Original
            </p>
            <p className="mono text-[13px] leading-[1.75] text-ink">
              Re:{" "}
              <mark className="rounded bg-accent-soft px-1 text-accent">Danielle Okafor</mark>, NHS{" "}
              <mark className="rounded bg-accent-soft px-1 text-accent">942 553 8021</mark>. Reviewed
              with her son, <mark className="rounded bg-accent-soft px-1 text-accent">Marcus</mark>.
            </p>
          </div>
          <div className="bg-bg/60 p-5">
            <p className="mb-3 text-[11px] font-semibold uppercase tracking-[0.14em] text-muted">
              De-identified
            </p>
            <p className="mono text-[13px] leading-[1.75] text-ink">
              Re: <span className="rounded bg-ink/90 px-1 text-surface">[PATIENT]</span>, NHS{" "}
              <span className="rounded bg-ink/90 px-1 text-surface">[NHS_NO]</span>. Reviewed with her
              son, <span className="rounded bg-ink/90 px-1 text-surface">[RELATIVE]</span>.
            </p>
          </div>
        </div>
      </div>
      <figcaption className="mt-3 px-1 text-[12.5px] leading-relaxed text-muted">
        The map from tokens back to real names stays in memory. It is never written to disk.
      </figcaption>
    </figure>
  );
}

function Hero() {
  return (
    <section id="top" className="mx-auto max-w-6xl px-5 pb-16 pt-12 sm:px-8 lg:pb-20 lg:pt-16">
      <div className="grid items-center gap-10 lg:grid-cols-[1.1fr_0.9fr] lg:gap-16">
        <div>
          <p className="rise rise-1 text-[12px] font-semibold uppercase tracking-[0.16em] text-accent">
            Building in the open
          </p>
          <h1 className="rise rise-2 mt-4 text-balance text-[1.9rem] font-semibold leading-[1.14] tracking-tight text-ink sm:text-[2.15rem] lg:text-[2.25rem]">
            AI for the paperwork.
            <br />
            Without the privacy trade-off.
          </h1>
          <p className="rise rise-3 mt-5 max-w-xl text-[15px] leading-relaxed text-muted sm:text-base">
            De-identification runs entirely on your machine. Only de-identified text is ever used to
            draft notes, so nothing identifying leaves the device.
          </p>
          <div className="rise rise-4 mt-8 flex flex-wrap items-center gap-3">
            <a
              href={REPO}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-2 rounded-xl bg-accent px-5 py-3 text-[14px] font-semibold text-white shadow-[0_6px_20px_rgba(79,70,229,0.28)] transition-all hover:-translate-y-px hover:bg-accent-hover"
            >
              View on GitHub
              <ArrowUpRight className="h-4 w-4" strokeWidth={2.25} aria-hidden />
            </a>
            <a
              href="#how"
              className="inline-flex items-center gap-2 rounded-xl border border-border bg-surface px-5 py-3 text-[14px] font-semibold text-ink transition-colors hover:bg-accent-soft"
            >
              How it works
              <ArrowRight className="h-4 w-4" strokeWidth={2.25} aria-hidden />
            </a>
          </div>
        </div>
        <RedactionVisual />
      </div>
    </section>
  );
}

const STEPS = [
  {
    title: "Strip identifiers locally",
    body: "Regex and on-device NER remove NHS numbers, names, addresses, and dates before anything else runs.",
  },
  {
    title: "Review and approve",
    body: "A clinician reads the redacted document and signs off. Nothing moves forward without that approval.",
  },
  {
    title: "Generate on safe text only",
    body: "Notes are drafted from de-identified text, by a local model or an API if you prefer. The map back to real identities stays in memory and is never written to disk.",
  },
];

function How() {
  return (
    <section id="how" className="border-t border-line bg-surface/60">
      <div className="mx-auto max-w-6xl px-5 py-16 sm:px-8 lg:py-20">
        <h2 className="text-[1.5rem] font-semibold tracking-tight text-ink sm:text-[1.75rem]">
          How it works
        </h2>
        <ol className="mt-8">
          {STEPS.map((step, i) => (
            <li
              key={step.title}
              className="grid gap-2 border-t border-line py-7 sm:grid-cols-[4rem_1fr] sm:gap-8"
            >
              <span className="mono text-[2rem] font-medium leading-none text-faint" aria-hidden>
                {String(i + 1).padStart(2, "0")}
              </span>
              <div className="max-w-2xl">
                <h3 className="text-[1.05rem] font-semibold text-ink">{step.title}</h3>
                <p className="mt-2 text-[14.5px] leading-relaxed text-muted">{step.body}</p>
              </div>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}

const GUARANTEES = [
  { icon: WifiOff, text: "No network calls in the de-identification stage." },
  { icon: FileCheck, text: "Only de-identified text is written to disk." },
  { icon: KeyRound, text: "The re-identification map stays in memory." },
  { icon: Trash2, text: "One action wipes every document and mapping." },
];

function Guarantee() {
  return (
    <section className="border-t border-line">
      <div className="mx-auto max-w-6xl px-5 py-16 sm:px-8 lg:py-20">
        <h2 className="text-[1.5rem] font-semibold tracking-tight text-ink sm:text-[1.75rem]">
          The privacy guarantee
        </h2>
        <p className="mt-3 max-w-xl text-[14.5px] leading-relaxed text-muted">
          The safety checks run on every document before it is written, so the guarantee does not
          depend on the reviewer having caught everything.
        </p>
        <div className="mt-8 max-w-2xl rounded-2xl border border-border bg-surface p-6 shadow-cs sm:p-7">
          <ul className="divide-y divide-line">
            {GUARANTEES.map(({ icon: Icon, text }) => (
              <li key={text} className="flex items-center gap-3 py-3.5 first:pt-0 last:pb-0">
                <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-accent-soft">
                  <Icon className="h-[18px] w-[18px] text-accent" strokeWidth={2} aria-hidden />
                </span>
                <span className="text-[14.5px] leading-relaxed text-ink">{text}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}

function Closing() {
  return (
    <section className="border-t border-line bg-surface/60">
      <div className="mx-auto flex max-w-6xl flex-col items-start gap-6 px-5 py-16 sm:flex-row sm:items-center sm:justify-between sm:px-8 lg:py-20">
        <div>
          <h2 className="text-[1.4rem] font-semibold tracking-tight text-ink sm:text-[1.6rem]">
            Clone it and run it offline.
          </h2>
          <p className="mt-2 max-w-md text-[14.5px] leading-relaxed text-muted">
            The de-identification layers, the review gate, and the tests are all in the open.
          </p>
        </div>
        <a
          href={REPO}
          target="_blank"
          rel="noreferrer"
          className="inline-flex shrink-0 items-center gap-2 rounded-xl bg-accent px-5 py-3 text-[14px] font-semibold text-white shadow-[0_6px_20px_rgba(79,70,229,0.28)] transition-all hover:-translate-y-px hover:bg-accent-hover"
        >
          View on GitHub
          <ArrowUpRight className="h-4 w-4" strokeWidth={2.25} aria-hidden />
        </a>
      </div>
    </section>
  );
}

function Footer() {
  return (
    <footer className="border-t border-line bg-surface/60">
      <div className="mx-auto flex max-w-6xl flex-col gap-6 px-5 py-12 sm:flex-row sm:items-center sm:justify-between sm:px-8">
        <div>
          <Wordmark className="text-[15px] text-ink" />
          <p className="mt-2 text-[13.5px] text-muted">Building in the open. Thoughts welcome.</p>
          <p className="mt-1 text-[12.5px] text-muted/80">De-identified on-device. Reviewed by a human.</p>
        </div>
        <a
          href={REPO}
          target="_blank"
          rel="noreferrer"
          className="inline-flex items-center gap-1.5 self-start text-[13.5px] font-medium text-accent transition-colors hover:text-accent-hover sm:self-auto"
        >
          View on GitHub
          <ArrowUpRight className="h-4 w-4" strokeWidth={2} aria-hidden />
        </a>
      </div>
    </footer>
  );
}

export default function App() {
  return (
    <>
      <Nav />
      <main>
        <Hero />
        <How />
        <Guarantee />
        <Closing />
      </main>
      <Footer />
    </>
  );
}
