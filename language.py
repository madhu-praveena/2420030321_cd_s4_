"""
A tiny C-like language:
  x = 10;
  y = x + 2 * 3;
  print(y);
  if (x < y) { print(x); } else { print(y); }
  while (x < 15) { x = x + 1; }

No Python eval/exec is used. The same lexer and parser feed two independent
execution paths: AST interpreter and bytecode compiler + virtual machine.
"""
from dataclasses import dataclass
from typing import Any

@dataclass
class Token:
    kind: str
    value: str
    pos: int

class LanguageError(Exception):
    pass

KEYWORDS = {"if": "IF", "else": "ELSE", "while": "WHILE", "print": "PRINT"}
TWO_CHAR = {"==", "!=", "<=", ">=", "&&", "||"}
ONE_CHAR = set("+-*/%(){};=<>!")

def lex(source: str):
    tokens = []
    i = 0
    while i < len(source):
        ch = source[i]
        if ch.isspace():
            i += 1
            continue
        if source.startswith("//", i):
            end = source.find("\n", i)
            i = len(source) if end == -1 else end
            continue
        if ch.isdigit():
            start = i
            while i < len(source) and source[i].isdigit():
                i += 1
            tokens.append(Token("NUMBER", source[start:i], start))
            continue
        if ch.isalpha() or ch == "_":
            start = i
            while i < len(source) and (source[i].isalnum() or source[i] == "_"):
                i += 1
            value = source[start:i]
            tokens.append(Token(KEYWORDS.get(value, "IDENT"), value, start))
            continue
        pair = source[i:i+2]
        if pair in TWO_CHAR:
            tokens.append(Token(pair, pair, i))
            i += 2
            continue
        if ch in ONE_CHAR:
            tokens.append(Token(ch, ch, i))
            i += 1
            continue
        raise LanguageError(f"Unexpected character {ch!r} at position {i}")
    tokens.append(Token("EOF", "", len(source)))
    return tokens

# AST nodes
@dataclass
class Number: value: int
@dataclass
class Variable: name: str
@dataclass
class Unary: op: str; expr: Any
@dataclass
class Binary: op: str; left: Any; right: Any
@dataclass
class Assign: name: str; expr: Any
@dataclass
class Print: expr: Any
@dataclass
class Block: statements: list
@dataclass
class If: condition: Any; then_branch: Any; else_branch: Any
@dataclass
class While: condition: Any; body: Any

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.i = 0

    def current(self): return self.tokens[self.i]
    def check(self, kind): return self.current().kind == kind
    def advance(self):
        t = self.current()
        if t.kind != "EOF": self.i += 1
        return t
    def expect(self, kind):
        if not self.check(kind):
            t = self.current()
            raise LanguageError(f"Expected {kind}, got {t.kind} ({t.value!r}) at position {t.pos}")
        return self.advance()

    def parse(self):
        statements = []
        while not self.check("EOF"):
            statements.append(self.statement())
        return Block(statements)

    def statement(self):
        if self.check("IDENT"):
            name = self.advance().value
            self.expect("=")
            expr = self.expression()
            self.expect(";")
            return Assign(name, expr)
        if self.check("PRINT"):
            self.advance(); self.expect("(")
            expr = self.expression()
            self.expect(")"); self.expect(";")
            return Print(expr)
        if self.check("IF"):
            self.advance(); self.expect("(")
            cond = self.expression(); self.expect(")")
            then_branch = self.statement()
            else_branch = None
            if self.check("ELSE"):
                self.advance()
                else_branch = self.statement()
            return If(cond, then_branch, else_branch)
        if self.check("WHILE"):
            self.advance(); self.expect("(")
            cond = self.expression(); self.expect(")")
            return While(cond, self.statement())
        if self.check("{"):
            self.advance()
            statements = []
            while not self.check("}") and not self.check("EOF"):
                statements.append(self.statement())
            self.expect("}")
            return Block(statements)
        t = self.current()
        raise LanguageError(f"Unexpected token {t.kind} ({t.value!r}) at position {t.pos}")

    # Precedence: OR, AND, equality, relation, add, multiply
    PRECEDENCE = {"||": 1, "&&": 2, "==": 3, "!=": 3,
                  "<": 4, "<=": 4, ">": 4, ">=": 4,
                  "+": 5, "-": 5, "*": 6, "/": 6, "%": 6}

    def expression(self, min_prec=1):
        if self.check("!") or self.check("-"):
            op = self.advance().kind
            left = Unary(op, self.expression(7))
        elif self.check("NUMBER"):
            left = Number(int(self.advance().value))
        elif self.check("IDENT"):
            left = Variable(self.advance().value)
        elif self.check("("):
            self.advance()
            left = self.expression()
            self.expect(")")
        else:
            t = self.current()
            raise LanguageError(f"Expected expression, got {t.kind} at position {t.pos}")

        while self.current().kind in self.PRECEDENCE:
            op = self.current().kind
            prec = self.PRECEDENCE[op]
            if prec < min_prec: break
            self.advance()
            right = self.expression(prec + 1)
            left = Binary(op, left, right)
        return left

def parse(tokens):
    return Parser(tokens).parse()

def eval_expr(node, env):
    if isinstance(node, Number): return node.value
    if isinstance(node, Variable):
        if node.name not in env: raise LanguageError(f"Undefined variable: {node.name}")
        return env[node.name]
    if isinstance(node, Unary):
        value = eval_expr(node.expr, env)
        return -value if node.op == "-" else int(not value)
    if isinstance(node, Binary):
        # Short-circuit Boolean evaluation
        left = eval_expr(node.left, env)
        if node.op == "&&": return int(bool(left) and bool(eval_expr(node.right, env)))
        if node.op == "||": return int(bool(left) or bool(eval_expr(node.right, env)))
        right = eval_expr(node.right, env)
        ops = {
            "+": lambda: left + right, "-": lambda: left - right,
            "*": lambda: left * right, "/": lambda: int(left / right),
            "%": lambda: left % right, "==": lambda: int(left == right),
            "!=": lambda: int(left != right), "<": lambda: int(left < right),
            "<=": lambda: int(left <= right), ">": lambda: int(left > right),
            ">=": lambda: int(left >= right)
        }
        if node.op == "/" and right == 0: raise LanguageError("Division by zero")
        if node.op == "%" and right == 0: raise LanguageError("Modulo by zero")
        return ops[node.op]()
    raise LanguageError("Unknown expression node")

def interpret(program):
    env, output = {}, []
    def run(stmt):
        if isinstance(stmt, Block):
            for s in stmt.statements: run(s)
        elif isinstance(stmt, Assign):
            env[stmt.name] = eval_expr(stmt.expr, env)
        elif isinstance(stmt, Print):
            output.append(str(eval_expr(stmt.expr, env)))
        elif isinstance(stmt, If):
            if eval_expr(stmt.condition, env): run(stmt.then_branch)
            elif stmt.else_branch is not None: run(stmt.else_branch)
        elif isinstance(stmt, While):
            iterations = 0
            while eval_expr(stmt.condition, env):
                run(stmt.body)
                iterations += 1
                if iterations > 100000: raise LanguageError("Loop limit exceeded (100000 iterations)")
        else: raise LanguageError("Unknown statement node")
    run(program)
    return {"output": output, "variables": env}

# Bytecode compiler and stack VM
class Compiler:
    def __init__(self):
        self.code = []
        self.next_label = 0
    def emit(self, op, arg=None):
        self.code.append([op, arg])
        return len(self.code) - 1
    def label(self):
        n = self.next_label; self.next_label += 1
        return f"L{n}"
    def mark(self, label):
        self.emit("LABEL", label)
    def expr(self, n):
        if isinstance(n, Number): self.emit("PUSH", n.value)
        elif isinstance(n, Variable): self.emit("LOAD", n.name)
        elif isinstance(n, Unary):
            self.expr(n.expr); self.emit("NEG" if n.op == "-" else "NOT")
        elif isinstance(n, Binary):
            if n.op == "&&":
                false_label, end_label = self.label(), self.label()
                self.expr(n.left); self.emit("JUMP_IF_FALSE", false_label)
                self.expr(n.right); self.emit("BOOL")
                self.emit("JUMP", end_label)
                self.mark(false_label); self.emit("PUSH", 0); self.mark(end_label)
            elif n.op == "||":
                true_label, end_label = self.label(), self.label()
                self.expr(n.left); self.emit("JUMP_IF_TRUE", true_label)
                self.expr(n.right); self.emit("BOOL")
                self.emit("JUMP", end_label)
                self.mark(true_label); self.emit("PUSH", 1); self.mark(end_label)
            else:
                self.expr(n.left); self.expr(n.right)
                mapping = {"+":"ADD","-":"SUB","*":"MUL","/":"DIV","%":"MOD",
                           "==":"EQ","!=":"NE","<":"LT","<=":"LE",">":"GT",">=":"GE"}
                self.emit(mapping[n.op])
        else: raise LanguageError("Unknown expression node")
    def stmt(self, n):
        if isinstance(n, Block):
            for s in n.statements: self.stmt(s)
        elif isinstance(n, Assign):
            self.expr(n.expr); self.emit("STORE", n.name)
        elif isinstance(n, Print):
            self.expr(n.expr); self.emit("PRINT")
        elif isinstance(n, If):
            else_label, end_label = self.label(), self.label()
            self.expr(n.condition); self.emit("JUMP_IF_FALSE", else_label)
            self.stmt(n.then_branch)
            if n.else_branch is not None:
                self.emit("JUMP", end_label); self.mark(else_label)
                self.stmt(n.else_branch); self.mark(end_label)
            else:
                self.mark(else_label)
        elif isinstance(n, While):
            start, end = self.label(), self.label()
            self.mark(start); self.expr(n.condition)
            self.emit("JUMP_IF_FALSE", end)
            self.stmt(n.body); self.emit("JUMP", start); self.mark(end)
        else: raise LanguageError("Unknown statement node")
        return self.code

def compile_program(program):
    c = Compiler()
    c.stmt(program)
    c.emit("HALT")
    return c.code

def run_vm(code):
    labels = {arg: i for i, (op, arg) in enumerate(code) if op == "LABEL"}
    env, stack, output = {}, [], []
    pc, steps = 0, 0
    binary = {
        "ADD": lambda a,b:a+b, "SUB":lambda a,b:a-b, "MUL":lambda a,b:a*b,
        "DIV":lambda a,b:int(a/b), "MOD":lambda a,b:a%b,
        "EQ":lambda a,b:int(a==b), "NE":lambda a,b:int(a!=b),
        "LT":lambda a,b:int(a<b), "LE":lambda a,b:int(a<=b),
        "GT":lambda a,b:int(a>b), "GE":lambda a,b:int(a>=b)
    }
    while pc < len(code):
        steps += 1
        if steps > 1000000: raise LanguageError("VM instruction limit exceeded")
        op, arg = code[pc]
        pc += 1
        if op == "PUSH": stack.append(arg)
        elif op == "LOAD":
            if arg not in env: raise LanguageError(f"Undefined variable: {arg}")
            stack.append(env[arg])
        elif op == "STORE": env[arg] = stack.pop()
        elif op in binary:
            b, a = stack.pop(), stack.pop()
            if op in ("DIV","MOD") and b == 0: raise LanguageError("Division by zero")
            stack.append(binary[op](a,b))
        elif op == "NEG": stack.append(-stack.pop())
        elif op == "NOT": stack.append(int(not stack.pop()))
        elif op == "BOOL": stack.append(int(bool(stack.pop())))
        elif op == "PRINT": output.append(str(stack.pop()))
        elif op == "JUMP": pc = labels[arg] + 1
        elif op == "JUMP_IF_FALSE":
            if not stack.pop(): pc = labels[arg] + 1
        elif op == "JUMP_IF_TRUE":
            if stack.pop(): pc = labels[arg] + 1
        elif op in ("LABEL",): pass
        elif op == "HALT": break
        else: raise LanguageError(f"Unknown instruction: {op}")
    return {"output": output, "variables": env, "steps": steps}

def format_code(code):
    lines = []
    for i, (op, arg) in enumerate(code):
        if op == "LABEL": lines.append(f"{arg}:")
        elif arg is None: lines.append(f"{i:03}  {op}")
        else: lines.append(f"{i:03}  {op} {arg}")
    return "\n".join(lines)
