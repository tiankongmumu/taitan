/**
 * ShipMicro Smoke Test Suite
 * ==========================
 * Runs after every Vercel deployment to verify all critical pages load correctly.
 * Exit code 0 = all tests pass, 1 = one or more failures.
 *
 * Usage:
 *   npx tsx scripts/smoke-test.ts                         # test production
 *   npx tsx scripts/smoke-test.ts https://preview.vercel.app  # test specific URL
 */

const BASE_URL = process.argv[2] || "https://www.shipmicro.com";

interface TestResult {
    name: string;
    url: string;
    passed: boolean;
    status?: number;
    detail?: string;
    durationMs: number;
}

async function fetchTest(name: string, path: string, checks?: {
    containsText?: string;
    notContainsText?: string;
    jsonCheck?: (data: Record<string, unknown>) => boolean;
}): Promise<TestResult> {
    const url = `${BASE_URL}${path}`;
    const start = Date.now();
    try {
        const res = await fetch(url, {
            headers: { "User-Agent": "ShipMicro-SmokeTest/1.0" },
            redirect: "follow",
        });
        const durationMs = Date.now() - start;
        const body = await res.text();

        if (!res.ok) {
            return { name, url, passed: false, status: res.status, detail: `HTTP ${res.status}`, durationMs };
        }

        if (checks?.containsText && !body.includes(checks.containsText)) {
            return { name, url, passed: false, status: res.status, detail: `Missing text: "${checks.containsText}"`, durationMs };
        }

        if (checks?.notContainsText && body.includes(checks.notContainsText)) {
            return { name, url, passed: false, status: res.status, detail: `Should NOT contain: "${checks.notContainsText}"`, durationMs };
        }

        if (checks?.jsonCheck) {
            try {
                const json = JSON.parse(body);
                if (!checks.jsonCheck(json)) {
                    return { name, url, passed: false, status: res.status, detail: `JSON assertion failed`, durationMs };
                }
            } catch {
                return { name, url, passed: false, status: res.status, detail: `Invalid JSON response`, durationMs };
            }
        }

        return { name, url, passed: true, status: res.status, durationMs };
    } catch (err) {
        return { name, url, passed: false, detail: `Network error: ${err instanceof Error ? err.message : String(err)}`, durationMs: Date.now() - start };
    }
}

async function runSmokeTests(): Promise<void> {
    console.log(`\n🔥 ShipMicro Smoke Test Suite`);
    console.log(`   Target: ${BASE_URL}`);
    console.log(`   Time: ${new Date().toISOString()}\n`);
    console.log("─".repeat(60));

    const tests: Promise<TestResult>[] = [
        fetchTest("Homepage", "/", { containsText: "ShipMicro" }),
        fetchTest("Tools List", "/tools", { containsText: "Free Developer Tools" }),
        fetchTest("Arcade List", "/arcade", { containsText: "games" }),
        fetchTest("Tool Detail: JSON Formatter", "/tools/json-formatter", { containsText: "JSON Formatter" }),
        fetchTest("Tool Detail: Pomodoro", "/tools/pomodoro", { containsText: "Pomodoro" }),
        fetchTest("Game Detail: Pong Duel", "/arcade/pong-duel", { containsText: "Pong Duel" }),
        fetchTest("Game Detail: Color Flood", "/arcade/color-flood", { containsText: "Color Flood" }),
        fetchTest("Pricing Page", "/pricing", { containsText: "Pro" }),
        fetchTest("Static: Game HTML", "/games/color-flood.html", { containsText: "Color Flood" }),
        fetchTest("Static: Tool HTML", "/tools/json-formatter.html", { containsText: "JSON" }),
        fetchTest("Health Check API", "/api/health", {
            jsonCheck: (data) =>
                data.status === "ok" &&
                typeof data.metrics === "object" &&
                (data.metrics as Record<string, unknown>).tools !== undefined &&
                Number((data.metrics as Record<string, unknown>).tools) > 0 &&
                Number((data.metrics as Record<string, unknown>).games) > 0,
        }),
        fetchTest("No Server Error on Homepage", "/", { notContainsText: "Application error" }),
    ];

    const results = await Promise.all(tests);

    let passCount = 0;
    let failCount = 0;

    for (const r of results) {
        const icon = r.passed ? "✅" : "❌";
        const status = r.status ? `[${r.status}]` : "[---]";
        const time = `${r.durationMs}ms`;
        console.log(`  ${icon} ${status} ${r.name.padEnd(35)} ${time.padStart(7)}${r.detail ? ` — ${r.detail}` : ""}`);
        if (r.passed) passCount++;
        else failCount++;
    }

    console.log("─".repeat(60));
    console.log(`\n  Results: ${passCount} passed, ${failCount} failed, ${results.length} total`);

    if (failCount > 0) {
        console.log("\n  ❌ SMOKE TEST FAILED — Production may be degraded!\n");
        process.exit(1);
    } else {
        console.log("\n  ✅ ALL SMOKE TESTS PASSED — Production is healthy!\n");
        process.exit(0);
    }
}

runSmokeTests();
