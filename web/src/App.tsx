const statusItems = [
  { label: 'Profile', value: 'coding' },
  { label: 'Source', value: 'results/results.csv' },
  { label: 'Mode', value: 'read-only' },
];

export default function App() {
  return (
    <main className="bg-surface text-ink min-h-screen">
      <section className="mx-auto flex min-h-screen max-w-5xl flex-col justify-center px-6 py-12">
        <div className="space-y-6">
          <p className="text-accent text-sm font-semibold tracking-wide uppercase">local-llm-lab</p>
          <h1 className="max-w-3xl text-4xl leading-tight font-semibold md:text-5xl">
            Local model evaluation dashboard foundation
          </h1>
          <p className="text-muted max-w-2xl text-base leading-7">
            Phase B UI work starts from React, TypeScript, Vite, and Tailwind CSS. The harness logic
            remains behind the API boundary.
          </p>
        </div>

        <dl className="mt-10 grid gap-4 sm:grid-cols-3">
          {statusItems.map((item) => (
            <div key={item.label} className="border-line bg-panel rounded border p-4">
              <dt className="text-muted text-xs font-medium tracking-wide uppercase">
                {item.label}
              </dt>
              <dd className="mt-2 text-lg font-semibold">{item.value}</dd>
            </div>
          ))}
        </dl>
      </section>
    </main>
  );
}
