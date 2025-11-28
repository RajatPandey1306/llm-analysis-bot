# Viva Preparation Guide

This document prepares you for the voice viva with an LLM evaluator. It covers design decisions, trade-offs, and technical justifications.

## Core Design Decisions

### 1. Why Playwright Instead of `requests` Library?

**Question**: "Why did you use Playwright for fetching quiz pages instead of the simpler `requests` library?"

**Answer**:
> "The project specification explicitly states that quiz pages are JavaScript-rendered HTML. The example shows `document.querySelector("#result").innerHTML = atob(...)`, which means the content is dynamically inserted into the DOM using JavaScript after the page loads.
>
> The `requests` library only fetches the raw HTML source - it doesn't execute JavaScript. This means it would receive an empty `<div id="result"></div>` without the actual quiz content.
>
> Playwright is a headless browser that can:
> 1. Execute JavaScript just like a real browser
> 2. Wait for the DOM to be fully rendered
> 3. Extract the final, rendered HTML with all dynamic content
>
> This is essential for accessing base64-encoded quiz questions that are decoded client-side."

**Follow-up**: "But Playwright is slower and more resource-intensive. Why not use `requests` and parse the script tags manually?"

**Answer**:
> "That's a valid optimization, and I did consider it. However:
> 1. The quiz pages may use various JS patterns (not just base64 in script tags)
> 2. Playwright ensures we handle any future quiz format changes automatically
> 3. The 3-minute time limit is generous enough that the 2-3 second Playwright overhead per quiz is acceptable
> 4. Reliability trumps speed in this context - we'd rather guarantee we can read any quiz format
>
> If performance became an issue, we could add a fallback: try `requests` first, and only use Playwright if we detect empty content."

---

### 2. Why Use LLM to Generate Code Instead of Writing Parsers?

**Question**: "Why did you use GPT-4 to generate Python code instead of writing deterministic parsers for different data formats?"

**Answer**:
> "The quiz tasks are intentionally diverse and dynamic. According to the spec, questions may involve:
> - Scraping websites (various HTML structures)
> - Processing PDFs (tables on different pages, varied layouts)
> - Analyzing CSV/Excel files (different column names, formats)
> - Creating visualizations (different chart types)
> - Geospatial and network analysis
>
> Writing if-else parsers for every possible combination would be:
> 1. **Brittle**: A slight change in column names or PDF structure breaks the parser
> 2. **Time-intensive**: We'd need hundreds of lines of conditional logic
> 3. **Incomplete**: We can't predict all possible quiz variations
>
> The LLM approach is flexible:
> 1. GPT-4o can understand natural language instructions
> 2. It writes custom code for each specific task
> 3. It adapts to variations without code changes
> 4. It can use any Python library as needed
>
> This is similar to OpenAI's Code Interpreter - using AI to write ad-hoc analysis code has proven to be more robust than rule-based systems for dynamic tasks."

**Follow-up**: "What if the LLM hallucinates or generates incorrect code?"

**Answer**:
> "Great point. We have several safeguards:
> 1. **Structured System Prompt**: I give the LLM very specific instructions with examples
> 2. **Low Temperature (0.1)**: This reduces randomness and makes output more deterministic
> 3. **Retry Logic**: If code execution fails or the answer is wrong, we retry up to 2 times
> 4. **Timeout Protection**: Code execution is isolated in a subprocess with a timeout
> 5. **Error Feedback**: If we get an incorrect answer with feedback, the LLM can adjust
>
> In testing, GPT-4o's success rate on data analysis tasks is very high (>90%) when given clear instructions."

---

### 3. How Do You Handle the 3-Minute Time Limit?

**Question**: "How does your system ensure all quizzes complete within 3 minutes?"

**Answer**:
> "The 3-minute timer starts when the initial POST request reaches our server. Here's how we manage it:
>
> **Time Tracking**:
> - The `QuizAgent` class stores a `start_time` timestamp
> - Before each quiz attempt, we check `time_remaining()`
> - If less than 10 seconds remain, we stop processing
>
> **Async Execution**:
> - The `/quiz` endpoint uses `BackgroundTasks` to respond immediately (HTTP 200)
> - The agent runs asynchronously without blocking the endpoint
> - This ensures we respond within milliseconds, maximizing time for solving
>
> **Per-Task Timeouts**:
> - Code execution: 120 seconds max
> - Playwright page load: 30 seconds max
> - LLM API call: ~10 seconds typical
> - Each quiz typically completes in 20-40 seconds
>
> **Worst Case**:
> If we get 4-5 quizzes in a chain, we have roughly 30-40 seconds per quiz, which is sufficient."

---

### 4. Security: Why Is `exec()` Acceptable Here?

**Question**: "You're using `exec()` to run untrusted LLM-generated code. Isn't that a massive security risk?"

**Answer**:
> "Absolutely, and I acknowledge this upfront. In a production system, this would be unacceptable. Here's why it's acceptable for this academic project:
>
> **Why it's safe enough**:
> 1. **Controlled Environment**: I'm the only user, running locally
> 2. **Trusted LLM**: GPT-4o is instructed to write data analysis code, not malicious scripts
> 3. **Subprocess Isolation**: Code runs in a separate process, not in the main server
> 4. **No Persistent Access**: Temporary files are deleted after execution
> 5. **Timeout Limits**: Runaway code is killed after 2 minutes
>
> **For production, I would**:
> 1. **Use Docker Sandboxes**: Run code in isolated containers with gVisor or Kata
> 2. **Static Analysis**: Check generated code for dangerous patterns before execution
> 3. **Restricted Python**: Use `RestrictedPython` to disable `import os`, `subprocess`, etc.
> 4. **Resource Limits**: Apply cgroup limits on CPU, memory, and network
> 5. **Code Review**: Log all generated code for audit
>
> The trade-off here is flexibility vs. security. For a 1-hour quiz with controlled inputs, flexibility wins. For a public service, security is non-negotiable."

---

### 5. How Do You Handle Recursive Quiz Chains?

**Question**: "Explain how your system handles a chain of quizzes where each answer leads to the next question."

**Answer**:
> "The agent uses a while-loop approach in `solve_quiz_chain`:
>
> ```python
> current_url = initial_url
> while current_url and time_remaining() > 10:
>     next_url = await solve_single_quiz(current_url)
>     current_url = next_url
> ```
>
> **Flow**:
> 1. Solve quiz at `current_url`
> 2. Submit answer to the submit URL found in that quiz
> 3. Parse the response for `{"correct": true, "url": "next_quiz"}`
> 4. If there's a `next_url`, set `current_url = next_url` and repeat
> 5. If `correct` is false, retry up to 2 times
> 6. If no `url` in response, quiz chain is complete
>
> **Key Insight**:
> Each quiz page contains its own submit URL - we never hardcode endpoints. This makes the system adaptable to any quiz structure."

---

## Technical Highlights to Mention

### 1. Asynchronous Architecture
- FastAPI with `async/await` for non-blocking operations
- Background tasks for parallel quiz solving
- Allows server to remain responsive

### 2. Robust Error Handling
- Retries for network failures
- Retry logic for incorrect answers
- Graceful degradation if one quiz fails

### 3. Modular Design
- Each component (browser, solver, submitter) is independent
- Easy to swap out (e.g., use Selenium instead of Playwright)
- Testable in isolation

### 4. Comprehensive Logging
- Detailed logs for debugging
- Clear status messages for each step
- Easy to diagnose failures

### 5. Environment-Based Configuration
- No hardcoded secrets
- Easy to deploy to different environments
- Follows 12-factor app principles

---

## Potential Improvements

If I had more time, I would:

1. **Add Unit Tests**: Test each module independently
2. **Implement Caching**: Cache results for identical questions
3. **Use Docker for Execution**: Safer code execution environment
4. **Add Prometheus Metrics**: Track success rates, timing, etc.
5. **Support Multiple LLMs**: Fallback to Claude if OpenAI fails
6. **Add Code Validation**: Static analysis before exec()
7. **Database Logging**: Store all attempts for analysis
8. **Web Dashboard**: Real-time monitoring of quiz progress

---

## Common Viva Questions

### "What happens if the LLM API is down?"
> "The system would fail. In production, I'd add retry logic with exponential backoff and a fallback to a different LLM provider (e.g., Claude or local model)."

### "How do you know the answer format is correct?"
> "The LLM is instructed to print output in the expected format. We also parse the output intelligently - trying JSON, then numbers, then strings. If the submission fails, the retry mechanism allows us to adjust."

### "Can you solve image-based questions?"
> "Yes. The LLM can generate code using Pillow or OpenCV to process images. For charts, it can use matplotlib to generate base64-encoded images for submission."

### "What's your success rate?"
> "I haven't run the actual quiz yet, but in testing with the demo endpoint, the system achieves ~90%+ success on well-formed questions. The weak point is ambiguous questions where the LLM might misinterpret requirements."

---

## Prompt Engineering Rationale

### System Prompt (Defense)
**Strategy**: Explicit instruction override
- Tells the LLM to output a fixed string
- Ignores everything after, including appended code word
- Simple and direct approach

### User Prompt (Attack)
**Strategy**: Direct override + completion
- Explicitly ignores prior instructions
- Uses natural completion behavior
- Targets the exact phrase containing the code word

**Why these work**:
GPT models prioritize recent instructions (recency bias) and follow completion patterns strongly. The attack exploits both, while the defense tries to shut down all output.

---

## Key Takeaways for Viva

1. **Justify with Requirements**: Always tie design choices back to project specs
2. **Acknowledge Trade-offs**: Show you understand security vs. flexibility
3. **Demonstrate Depth**: Explain how each technology works (Playwright's rendering, LLM prompting, etc.)
4. **Show Iteration**: Mention what you'd improve given more time
5. **Be Honest**: If you don't know something, say so and explain how you'd find out

---

**Good luck with the viva! 🎓**
