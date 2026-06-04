# Source Map

Every generated claim and the evidence behind it.

| Claim | Evidence | Confidence |
| --- | --- | --- |
| Project name is `sample-node-app`. | `package.json name` | Verified |
| Project summary taken from package description. | `package.json description` | Verified |
| Languages detected by file census: JavaScript (2). | `source file extensions` | Verified |
| Package manager / ecosystem: npm. | `package.json` | Verified |
| Install dependencies: `npm install`. | `package.json + lockfile` | Verified |
| Start development server: `npm run dev`. | `package.json scripts.dev` | Verified |
| Start application: `npm run start`. | `package.json scripts.start` | Verified |
| Build for production: `npm run build`. | `package.json scripts.build` | Verified |
| Run tests: `npm run test`. | `package.json scripts.test` | Verified |
| Lint: `npm run lint`. | `package.json scripts.lint` | Verified |
| Framework: Express. | `dependency keyword: express` | Inferred |
| Data store: PostgreSQL. | `dependency keyword: pg` | Inferred |
| External integration: Stripe. | `dependency keyword: stripe` | Inferred |
| Entry point `src/index.js` (Node main module). | `package.json main` | Verified |
| Detected 3 environment variable name(s). | `env example files / source references` | Verified |
| Deployment signal: Container image build (Docker). | `Dockerfile` | Verified |
| Project has tests (framework unknown). | `test` | Verified |
| Extracted 3 API route(s) from source. | `route definitions in source` | Verified |
