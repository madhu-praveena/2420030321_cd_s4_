import time
from language import lex, parse, interpret, compile_program, run_vm, format_code, LanguageError

def timed(fn):
    start = time.perf_counter()
    result = fn()
    return result, (time.perf_counter() - start) * 1000.0

def run_comparison(source):
    # Interpreter path: its own lexical and parsing pass
    it_tokens, it_lex_ms = timed(lambda: lex(source))
    it_ast, it_parse_ms = timed(lambda: parse(it_tokens))
    it_result, it_exec_ms = timed(lambda: interpret(it_ast))

    # Compiler/VM path: independent lexical and parsing pass, then translation
    vm_tokens, vm_lex_ms = timed(lambda: lex(source))
    vm_ast, vm_parse_ms = timed(lambda: parse(vm_tokens))
    bytecode, translate_ms = timed(lambda: compile_program(vm_ast))
    vm_result, vm_exec_ms = timed(lambda: run_vm(bytecode))

    correct = it_result["output"] == vm_result["output"] and it_result["variables"] == vm_result["variables"]
    return {
        "correct": correct,
        "interpreter": {
            "lex_ms": it_lex_ms, "parse_ms": it_parse_ms,
            "translation_ms": None, "execution_ms": it_exec_ms,
            "total_ms": it_lex_ms + it_parse_ms + it_exec_ms,
            "output": it_result["output"], "variables": it_result["variables"],
            "instruction_count": None
        },
        "vm": {
            "lex_ms": vm_lex_ms, "parse_ms": vm_parse_ms,
            "translation_ms": translate_ms, "execution_ms": vm_exec_ms,
            "total_ms": vm_lex_ms + vm_parse_ms + translate_ms + vm_exec_ms,
            "output": vm_result["output"], "variables": vm_result["variables"],
            "instruction_count": len(bytecode), "executed_steps": vm_result["steps"],
            "bytecode": format_code(bytecode)
        },
        "explanation": explain(it_exec_ms, translate_ms, vm_exec_ms, len(bytecode))
    }

def explain(interpreter_ms, translation_ms, vm_ms, instruction_count):
    if translation_ms + vm_ms < interpreter_ms:
        comparison = "For this run, translation plus VM execution took less time than direct AST evaluation."
    else:
        comparison = "For this run, translation plus VM execution took more time than direct AST evaluation; translation overhead may dominate for a small program."
    return (comparison + f" The VM generated {instruction_count} instructions. "
            "These timings are measurements of this implementation on the current machine, not a universal rule about all interpreters and compilers.")

def run_batch(programs):
    results = []
    for name, source in programs:
        try:
            results.append({"name": name, "source": source, "result": run_comparison(source), "error": None})
        except Exception as exc:
            results.append({"name": name, "source": source, "result": None, "error": str(exc)})
    return results
