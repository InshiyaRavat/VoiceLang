######### IMPORTS ###########
from string_with_arrows import *

######### CONSTANTS #########
DIGITS = '0123456789'

######### ARITHEMATIC OPERATOR #####
ARITHMETIC_OPERATOR = 'adADsubtrcSUBTRCmlipyMLIPYveVE'

######### ERROR #############
class Error:
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name=error_name
        self.details = details

    def as_string(self):
        result = f'{self.error_name}:{self.details}'
        result += f'\nFile {self.pos_start.fn}, Line {self.pos_start.ln + 1}'
        result += '\n\n' + string_with_arrow(self.pos_start.ftxt,self.pos_start,self.pos_end)
        return result

class IllegalCharError(Error):
    def __init__(self,pos_start,pos_end,details):
        super().__init__(pos_start, pos_end,'Illegal Character Error',details)

class IllegalOperatorError(Error):
    def __init__(self,pos_start,pos_end,details):
        super().__init__(pos_start, pos_end,'Illegal Operator Error',details)

class InvalidSyntaxError(Error):
    def __init__(self,pos_start,pos_end,details=''):
        super().__init__(pos_start, pos_end,'Invalid Syntax',details)

######### POSITION ##########
class Position:
    def __init__(self,idx,ln,col,fn ,ftxt):
        self.idx = idx
        self.ln = ln
        self.col = col
        #fn is file name and ftxt is file text
        self.fn = fn
        self.ftxt = ftxt 

    def advance(self,current_char=None):
        self.idx += 1
        self.col += 1

        if current_char == '\n':
            self.ln += 1
            self.col = 0
        return self
    
    def copy(self):
        return Position(self.idx,self.ln,self.col,self.fn,self.ftxt)

######### TOKENS ############
#TT means token type
TT_INT = 'INT'
TT_FLOAT = 'FLOAT'
TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_MUL = 'MUL'
TT_DIV = 'DIV'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'
TT_EOF = 'EOF'
class Token:
    def __init__(self,type_,value=None,pos_start=None,pos_end=None):
        self.type = type_
        self.value = value

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()
        
        if pos_end:
            self.pos_end = pos_end
    
    def __repr__(self):
        if self.value: return f'{self.type}:{self.value}'
        return f'{self.type}'
    
######## LEXER ############

class Lexer:
    def __init__(self,fn ,text):
        self.fn = fn
        self.text = text
        #starting with -1 and not zero because advance method will increment by 1 ,i.e. -1+1=0
        self.pos = Position(-1,0,-1,fn,text)
        self.current_char = None
        self.advance()

    def advance(self):
        #this method advance to the next character of the text
        self.pos.advance(self.current_char)
        #set current character as the character pointed by pos if pos<length else none means we reached the end of text
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

    def make_tokens(self):
        tokens=[]

        while self.current_char != None:
            if self.current_char in '\t' or self.current_char == ' ':
                self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            elif self.current_char =='+':
                tokens.append(Token(TT_PLUS,pos_start=self.pos))
                self.advance()
            elif self.current_char =='-':
                tokens.append(Token(TT_MINUS,pos_start=self.pos))
                self.advance()
            elif self.current_char =='x':
                tokens.append(Token(TT_MUL,pos_start=self.pos))
                self.advance()
            elif self.current_char =='/':
                tokens.append(Token(TT_DIV,pos_start=self.pos))
                self.advance()
            elif self.current_char == '(' :
                tokens.append(Token(TT_LPAREN,pos_start=self.pos))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN,pos_start=self.pos))
                self.advance()
            else:
                #return some error
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [] , IllegalCharError(pos_start,self.pos,"'"+char+"'")
        tokens.append(Token(TT_EOF,pos_start=self.pos))
        return tokens,None
    
    def make_number(self):
        num_str = ''
        #if there are no dots in the number then it is an integer and if dot_cnt = 1 then it is float
        dot_cnt = 0
        pos_start = self.pos.copy()

        while self.current_char is not None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_cnt == 1: break
                dot_cnt += 1
                num_str += '.'
            else:
                num_str += self.current_char
            self.advance()
        
        if dot_cnt == 0:
            return Token(TT_INT,int(num_str),pos_start,self.pos)
        else:
            return Token(TT_FLOAT,float(num_str),pos_start,self.pos)
        

################## NODES ###############
class NumberNode:
    def __init__(self,tok):
        self.tok=tok
        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end
    
    def __repr__(self):
        return f'{self.tok}'

class BinOpNode:
    def __init__(self,left_node,op_tok,right_node):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node
        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end
    def __repr__(self):
        return f'({self.left_node} , {self.op_tok} , {self.right_node})'

class UnaryOpNode:
    def __init__(self,op_tok,node):
        self.op_tok = op_tok
        self.node = node
        self.pos_start = self.op_tok.pos_start
        self.pos_end = node.pos_end
    
    def __repr__(self):
        return f'({self.op_tok}, {self.node})'
################### PARSE RESULT ###############

class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None

    def register(self , res):
        if isinstance(res,ParseResult):
            if res.error: self.error = res.error
            return res.node
        return res

    def success(self,node):
        self.node = node
        return self

    def failure(self,error):
        self.error = error
        return self
    
#################### PARSER ######################

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = -1
        self.advance()

    def advance(self):
        self.tok_idx += 1
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok
    
    ##################
    
    def parse(self):
        res = self.expr()  # Start by parsing an expr
        if not res.error and self.current_tok.type != TT_EOF:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start,self.current_tok.pos_end,
                "Expected '+' , '-' , '*' , '/'"
            ))
        return res
    
    def factor(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TT_PLUS,TT_MINUS): 
            res.register(self.advance())
            factor = res.register(self.factor())
            if res.error: return res
            return res.success(UnaryOpNode(tok , factor))
        elif tok.type in (TT_INT,TT_FLOAT):
            res.register(self.advance())  # Consume the token
            return res.success(NumberNode(tok))
        elif tok.type == TT_LPAREN:
            res.register(self.advance())
            expr = res.register(self.expr())
            if res.error : return res
            if self.current_tok.type == TT_RPAREN:
                res.register(self.advance())
                return res.success(expr)
            else:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected ')'"
                ))
        return res.failure(InvalidSyntaxError(
            tok.pos_start,tok.pos_end,
            "Expected int or float"
        ))
        
    def term(self):
        return self.bin_op(self.factor,(TT_MUL,TT_DIV))

    def expr(self):
        return self.bin_op(self.term,(TT_PLUS,TT_MINUS))
    
    ################# 

    def bin_op(self,func,ops):
        res = ParseResult()
        left = res.register(func())
        if res.error:return res

        while self.current_tok.type in ops:
            op_tok = self.current_tok
            res.register(self.advance())
            right = res.register(func())
            if res.error : return res
            left = BinOpNode(left,op_tok,right)
        return res.success(left)
    
################# VALUES ###############

class Number:
    def __init__(self,value):
        self.value = value
        self.set_pos() #to set position so that we can know about the divide by zero and such exceptions

    def set_pos(self,pos_start=None,pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self
    
    def added_to(self,other):
        if isinstance(other,Number):
            return Number(self.value + other.value)    

    def subbed_by(self,other):
        if isinstance(other,Number):
            return Number(self.value - other.value) 
        
    def multed_by(self,other):
        if isinstance(other,Number):
            return Number(self.value * other.value)  
        
    def dived_by(self,other):
        if isinstance(other,Number):
            return Number(self.value / other.value) 

    def __repr__(self):
         return str(self.value)

################# INTERPRETER ##########
class Interpreter:
    #this method visit process the passed node and then visit all its child nodes
    def visit(self, node):
        #if the node type is binary operator then it will assign visit_binaryOp to method_name, similarly if type is number node then visit_numberNode assigned to method_name
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self,method_name,self.no_visit_method)
        #no_visit_method is the method that will be called if no method_name is found
        return method(node)
    
    def no_visit_method(self,node):
        raise Exception(f'No visit_{type(node).__name__} method defined')
    
    #####################################

    def visit_NumberNode(self,node):
        return Number(node.tok.value).set_pos(node.pos_start,node.pos_end)

    def visit_BinOpNode(self,node):
        left = self.visit(node.left_node)
        right = self.visit(node.right_node)
        if node.op_tok.type == TT_PLUS:
            result = left.added_to(right)
        elif node.op_tok.type == TT_MINUS:
            result = left.subbed_by(right)
        elif node.op_tok.type == TT_MUL:
            result = left.multed_by(right)
        elif node.op_tok.type == TT_DIV:
            result = left.dived_by(right)

        return result.set_pos(node.pos_start,node.pos_end)

    def visit_UnaryOpNode(self,node):
        number = self.visit(node.node)

        if node.op_tok.type == TT_MINUS:
            number = number.multed_by(Number(-1)) #we multiply the number by -1 so that it becomes -{number}

        return number.set_pos(node.pos_start,node.pos_end)


             
################## RUN #################
def run(fn , text):
    lexer = Lexer(fn , text)
    tokens,error = lexer.make_tokens()

    if error: return None,error

    #### GENERATE AST #####
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error: return None,ast.error

    ## run program ##
    interpreter = Interpreter()
    result = interpreter.visit(ast.node)
    # return tokens,error
    # return ast.node,ast.error
    return result,None