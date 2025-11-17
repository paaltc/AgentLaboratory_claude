# AI Research Lab Workflow

You are conducting autonomous ML research on: **$ARGUMENTS**

## Your Role
You are an AI researcher executing a multi-phase research workflow. Follow the structured process below.

## Workflow Phases

### Phase 1: Literature Review
1. Use `Bash` to run: `python run_claude_research.py --topic "$ARGUMENTS" --no-api`
2. This will show the current task for Literature Review
3. Execute the task:
   - Use `WebSearch` to find relevant papers (e.g., "arxiv $ARGUMENTS machine learning")
   - Use `WebFetch` to get paper details from arxiv.org
   - Use `Write` to save your literature review to the specified output file

### Phase 2: Plan Formulation
1. After completing literature review, run the command again to get the next task
2. Read the literature review using `Read`
3. Formulate a research plan based on gaps identified
4. Save the plan using `Write`

### Phase 3: Data Preparation
1. Run the command again to get the data preparation task
2. Use `WebSearch` to find datasets on Hugging Face
3. Evaluate dataset suitability
4. Document dataset information using `Write`

### Phase 4: Experimentation
1. Get the experimentation task
2. Write ML experiment code using `Write`
3. Run experiments using `Bash` (e.g., `python experiment_code.py`)
4. Save results using `Write`

### Phase 5: Paper Writing
1. Get the paper writing task
2. Read all previous artifacts using `Read`
3. Write a complete LaTeX research paper
4. Save using `Write`

## Execution Instructions

1. **Start by running**:
```bash
python run_claude_research.py --topic "$ARGUMENTS" --no-api
```

2. **Follow the task instructions** displayed by the command
3. **Use your native tools** (WebSearch, WebFetch, Bash, Read, Write, Edit) to complete each task
4. **Save outputs** to the specified files in the results directory
5. **Run the command again** to advance to the next phase
6. **Repeat** until all phases are complete

## Important Notes
- Each phase depends on the previous one completing successfully
- Output files must be saved to the exact paths specified
- Use `--status` flag to check progress: `python run_claude_research.py --topic "$ARGUMENTS" --no-api --status`
- Use `--reset` to start over: `python run_claude_research.py --topic "$ARGUMENTS" --no-api --reset`

## Begin Now
Please start by running the initialization command to see your first task.
