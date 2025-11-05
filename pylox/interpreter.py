from typing import cast, Optional
from pylox.expr import Expr, Literal, Grouping, Unary, Binary, Ternary, Variable, Assign, Logical, Call, Lambda, Get, Set, This, Super
from pylox.tokentype import TokenType
from pylox.tokens import Token
from pylox.runtime_error import PyloxRuntimeError
from pylox.error import ErrorReporter
from pylox.stmt import Stmt, Expression, Print, Var, Block, If, While, Break, Function, Return, Class
from pylox.environment import Environment, UnInitValue
from pylox.lox_callable import LoxCallable, Clock
from pylox.lox_function import LoxFunction
from pylox.lox_class import LoxClass
from pylox.lox_instance import LoxInstance
from pylox.control_flow_signal import ReturnSignal, BreakSignal

class Interpreter:
    globals: Environment = Environment()
    __environment: Environment = globals 
    locals: dict[Expr, tuple[int, int]] = {} # values are (depth, unique_idx)
    global_idxs: dict[str, int] = {} # key:value -> global_var_name:unique_idx
    global_var_count: int = 0

    # globals.define("clock", Clock())
    global_idxs["clock"] = global_var_count
    global_var_count += 1
    globals.define(Clock())

    def interpret(self, statements: list[Stmt]):
        try:
            for statement in statements: 
                assert statement is not None
                self.execute(statement)
        except PyloxRuntimeError as error: ErrorReporter.runtime_error(error)

    def execute(self, stmt: Stmt) -> None:
        # if stmt is None: return
        stmt.accept(self)

    def resolve(self, expr: Expr, depth: int, unique_idx: int) -> None:
        self.locals[expr] = (depth, unique_idx)

    def execute_block(self, statements: list[Stmt | None], environment: Environment) -> None:
        previous: Environment = self.__environment
        try:
            self.__environment = environment
            for statement in statements: 
                if statement is not None: self.execute(statement)
        finally: self.__environment = previous

    def visit_Block_Stmt(self, stmt: Block) -> None:
        self.execute_block(stmt.statements, Environment(self.__environment))

    def visit_Class_Stmt(self, stmt: Class) -> None:
        superclasses: list[object] = []
        if stmt.superclasses:
            superclasses = [self.evaluate(sc) for sc in stmt.superclasses]
            if not all([isinstance(sc, LoxClass) for sc in superclasses]): raise PyloxRuntimeError(stmt.superclass.name, "Superclass must be a class.")
        self.global_idxs[stmt.name.lexeme] = self.global_var_count
        self.global_var_count += 1
        self.__environment.define(None)
        if stmt.superclasses:
            self.__environment = Environment(self.__environment)
            self.__environment.define(superclasses) # this is runtime(list[LoxClass]) of super
        methods: dict[str, LoxFunction] = {}
        class_methods: dict[str, LoxFunction] = {}
        for method in stmt.methods:
            function: LoxFunction = LoxFunction(method, self.__environment, method.name.lexeme == "init")
            methods[method.name.lexeme] = function
        for class_method in stmt.class_methods:
            function: LoxFunction = LoxFunction(class_method, self.__environment, False)
            class_methods[class_method.name.lexeme] = function
        mro = []
        klass: LoxClass = LoxClass(stmt.name.lexeme, superclasses, methods, mro)
        klass.fields = class_methods
        klass.mro = self.mro(klass, stmt.name)
        if superclasses: self.__environment = self.__environment.enclosing
        self.__environment.assign(stmt.name, klass, self.global_idxs[stmt.name.lexeme])

    # C3 algorithm for MRO(method resolution order) similar to python
    # key rules:
    # 1. A class must precede its base classes (parents) in the MRO.
    # 2. If a class C1 precedes a class C2 in the MRO of some class, then C1 must also precede C2 in the MRO of any subclass of that class. This rule prevents ambiguous or contradictory inheritance orders.
    def mro(self, klass: LoxClass, token: Token) -> list[LoxClass]:
        if not klass.superclasses: return [klass]
        return [klass] + self.merge([list(sc.mro) for sc in klass.superclasses] + [list(klass.superclasses)], token)

    def merge(self, mro_list: list[list[LoxClass]], token: Token) -> list[LoxClass]:
        res = []
        bad_head = False
        h = 0
        while mro_list:
            if not (h < len(mro_list)):
                raise PyloxRuntimeError(token, "Cannot create a consistent MRO.")
            if any(x == [] for x in mro_list): break
            head = mro_list[h][0]
            for i in range(0, len(mro_list)):
                if len(mro_list[i]) > 1 and head in mro_list[i][1:]: 
                    bad_head = True
                    break
            if bad_head:
                h = h + 1
                bad_head = False
                continue
            for i in range(len(mro_list)):
                if len(mro_list[i]) >= 1 and mro_list[i][0] == head: del mro_list[i][0]
            k = 0
            while k < len(mro_list):
                if not mro_list[k]:
                    del mro_list[k]
                    continue
                k = k + 1 
            res.append(head)
            h = 0
        return res

    def stringify(self, obj: object) -> str:
        if obj is None and not ErrorReporter.had_error: return "nil"
        if isinstance(obj, float):
            text: str = str(obj)
            if text[-2:] == ".0": text = text[:-2]
            return text
        if isinstance(obj, bool):
            if bool(obj): return "true" # python has True and False (capitalized T and F), Pylox has true and false
            return "false"
        return str(obj)

    def visit_Literal_Expr(self, expr: Literal) -> object:
        return expr.value
    
    def visit_Logical_Expr(self, expr: Logical) -> object:
        left: object = self.evaluate(expr.left)
        if expr.operator.token_type == TokenType.OR and self.is_truthy(left): return left
        if expr.operator.token_type == TokenType.AND and not self.is_truthy(left): return left
        return self.evaluate(expr.right) # a logic operator merely guarantees it will return a value with appropriate truthiness
    
    def visit_Set_Expr(self, expr: Set) -> object:
        obj: object = self.evaluate(expr.obj)
        if not isinstance(obj, LoxInstance): raise PyloxRuntimeError(expr.name, "Only instances have fields.")
        value: object = self.evaluate(expr.value)
        obj.set(expr.name, value)
        return value
    
    def visit_Super_Expr(self, expr: Super) -> object:
        distance, unique_idx = self.locals.get(expr)
        superclasses: list[LoxClass] = self.__environment.get_at(distance, "super", unique_idx)
        object: LoxInstance = self.__environment.get_at(distance - 1, "this", idx=0) # 'this' will be at 0th index as created at resolving class stmt
        method: Optional[LoxFunction] = None
        for sc in superclasses:
            if (loxfunc := sc.find_method(expr.method.lexeme)) is not None:
                method = loxfunc
                break
        if method is None: raise PyloxRuntimeError(expr.method, f"Undefined pproperty '{expr.method.lexeme}'.")
        return method.bind(object)

    def visit_This_Expr(self, expr: This) -> object:
        return self.lookup_variable(expr.keyword, expr)
    
    def visit_Grouping_Expr(self, expr: Grouping) -> object:
        return self.evaluate(expr.expression)
    
    def evaluate(self, expr: Optional[Expr]) -> object:
        if isinstance(expr, Expr): return expr.accept(self)
        return None

    def visit_Unary_Expr(self, expr: Unary) -> object:
        right: object = self.evaluate(expr.right)
        match expr.operator.token_type:
            case TokenType.MINUS:
                self.check_number_operand(expr.operator, right)
                return -float(cast(float, right)) # making mypy happy with cast
            case TokenType.BANG: return not self.is_truthy(right)
            case _: return None

    def is_truthy(self, obj: object) -> bool: # in pylox, except False and None everything else in truthy 
        if obj is None: return False
        if isinstance(obj, bool): return bool(obj)
        return True
    
    def visit_Binary_Expr(self, expr: Binary) -> object:
        left: object = self.evaluate(expr.left)
        right: object = self.evaluate(expr.right)
        match expr.operator.token_type:
            case TokenType.MINUS: 
                self.check_number_operands(expr.operator, left, right)
                return float(cast(float, left)) - float(cast(float, right))
            case TokenType.PLUS:
                if isinstance(left, float) and isinstance(right, float): return float(left) + float(right)
                if isinstance(left, str) or isinstance(right, str): 
                    return (str(left)[:-2] if isinstance(left, float) else str(left)) + (str(right)[:-2] if isinstance(right, float) else str(right))
                raise PyloxRuntimeError(expr.operator, "Operands must be numbers or strings.")
            case TokenType.SLASH: 
                self.check_number_operands(expr.operator, left, right)
                if float(cast(float, right)) == 0: raise PyloxRuntimeError(expr.operator, "Cannot divide by zero.")
                return float(cast(float, left)) / float(cast(float, right))
            case TokenType.STAR: 
                self.check_number_operands(expr.operator, left, right)
                return float(cast(float, left)) * float(cast(float, right))
            case TokenType.GREATER:
                self.check_number_operands(expr.operator, left, right)  
                return float(cast(float, left)) > float(cast(float, right))
            case TokenType.GREATER_EQUAL: 
                self.check_number_operands(expr.operator, left, right)
                return float(cast(float, left)) >= float(cast(float, right))
            case TokenType.LESS: 
                self.check_number_operands(expr.operator, left, right)
                return float(cast(float, left)) < float(cast(float, right))
            case TokenType.LESS_EQUAL: 
                self.check_number_operands(expr.operator, left, right)
                return float(cast(float, left)) <= float(cast(float, right))
            case TokenType.BANG_EQUAL: return not self.is_equal(left, right) # can just use left == right here
            case TokenType.EQUAL_EQUAL: return self.is_equal(left, right) # can just use left != right here
            case _: return None

    def visit_Call_Expr(self, expr: Call) -> object:
        callee: object = self.evaluate(expr.callee)
        arguments: list[object] = []
        for argument in expr.arguments: arguments.append(self.evaluate(argument))
        if not isinstance(callee, LoxCallable): raise PyloxRuntimeError(expr.paren, "Can only call functions and classes.")
        function: LoxCallable = callee
        if len(arguments) != function.arity(): raise PyloxRuntimeError(expr.paren, f"Expected {function.arity()} arguments but got {len(arguments)}.")
        return function.call(self, arguments)
    
    def visit_Get_Expr(self, expr: Get) -> object:
        obj: object = self.evaluate(expr.obj)
        if isinstance(obj, LoxInstance):
            res = obj.get(expr.name)
            if isinstance(res, LoxFunction) and res.declaration.is_getter: return res.call(self, [])
            return res
        raise PyloxRuntimeError(expr.name, "Only instances have properties.")

    def is_equal(self, a: object, b: object) -> bool: # this func is not needed (in python) but reminds me ow a different lang like java would need it as lox hhandles equality differently from it
        if a is None and b is None: return True
        if a is None: return False
        return a == b
    
    def check_number_operand(self, operator: Token, operand: object):
        if isinstance(operand, float): return
        raise PyloxRuntimeError(operator, "Operand must be a number.")
    
    def check_number_operands(self, operator: Token, left: object, right: object):
        if isinstance(left, float) and isinstance(right, float): return
        raise PyloxRuntimeError(operator, "Operands must be numbers.")
    
    def visit_Ternary_Expr(self, expr: Ternary) -> object:
        condition_eval: object = self.evaluate(expr.condition)
        if self.is_truthy(condition_eval): return self.evaluate(expr.expr_if_true)
        return self.evaluate(expr.expr_if_false)
    
    def visit_Variable_Expr(self, expr: Variable) -> object: 
        return self.lookup_variable(expr.name, expr)
    
    def lookup_variable(self, name: Token, expr: Expr) -> object:
        distance, unique_idx = self.locals.get(expr) if self.locals.get(expr) else (None, None)
        if distance is not None: return self.__environment.get_at(distance, name.lexeme, unique_idx)
        return self.globals.get(name, self.global_idxs[name.lexeme])
    
    def visit_Expression_Stmt(self, stmt: Expression) -> None: self.evaluate(stmt.expression)

    def visit_Function_Stmt(self, stmt: Function) -> None:
        function: LoxFunction = LoxFunction(stmt, self.__environment, False)
        self.__environment.define(function)
        if self.__environment.enclosing is None:
            self.global_idxs[stmt.name.lexeme] = self.global_var_count
            self.global_var_count += 1

    def visit_If_Stmt(self, stmt: If) -> None:
        if self.is_truthy(self.evaluate(stmt.condition)): self.execute(stmt.then_branch)
        elif stmt.else_branch is not None: self.execute(stmt.else_branch)
    
    def visit_Print_Stmt(self, stmt: Print) -> None:
        value: object = self.evaluate(stmt.expression)
        print(self.stringify(value))

    def visit_Return_Stmt(self, stmt: Return) -> None:
        value: object = None
        if stmt.value is not None: value = self.evaluate(stmt.value)
        raise ReturnSignal(value)

    def visit_Var_Stmt(self, stmt: Var) -> None:
        value: object | UnInitValue = UnInitValue()
        if not isinstance(stmt.initializer, UnInitValue): value = self.evaluate(stmt.initializer) 
        self.__environment.define(value)
        if self.__environment.enclosing is None:
            self.global_idxs[stmt.name.lexeme] = self.global_var_count
            self.global_var_count += 1

    def visit_While_Stmt(self, stmt: While) -> None:
        while self.is_truthy(self.evaluate(stmt.condition)):
            try: self.execute(stmt.body)
            except BreakSignal: break # TODO: implement pylox break withhout using python break

    def visit_Break_Stmt(self, stmt: Break) -> None:
        raise BreakSignal

    def visit_Assign_Expr(self, expr: Assign) -> object:
        value: object = self.evaluate(expr.value)
        # self.__environment.assign(expr.name, value)
        distance, unique_idx = self.locals.get(expr) if self.locals.get(expr) else (None, None)
        if distance is not None: self.__environment.assign_at(distance, unique_idx, value)
        else: self.globals.assign(expr.name, value, self.global_idxs[expr.name.lexeme])
        return value # assignment is an expression that can be nested inside other expressions
    
    def visit_Lambda_Expr(self, expr: Lambda) -> LoxFunction:
        function: LoxFunction = LoxFunction(expr, self.__environment)
        return function

