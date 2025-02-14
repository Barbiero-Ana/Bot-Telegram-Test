positv = ['bom', 'ótimo', 'excelente', 'adoro', 'amei', 'gostei', 'maravilhoso', 'satisfeito', 'perfeito', 'contente', 'adorei']
negativ = ['ruim', 'péssimo', 'horrível', 'desapontado', 'não gostei', 'decepcionado', 'terrível', 'odiei']
negacao = ['não', 'nunca', 'jamais']
intens = ['muito', 'extremamente', 'pouco']

def process(texto):
    pontos = ['.', ',', '!', '?', ';', ':', '(', ')', '[', ']', '{', '}', '...', '..']
    for ponto in pontos:
        texto = texto.replace(ponto, '')
    texto = texto.lower()
    palavras = texto.split()
    return palavras

def analisar(texto):
    palavras = process(texto)
    positivo = 0
    negativo = 0
    negation = False
    intensificador = 1
    
    for palavra in palavras:
        if palavra in intens:
            if palavra == 'muito' or palavra == 'extremamente':
                intensificador = 2
            elif palavra == 'pouco':
                intensificador = 0.5
            continue
        
        if palavra in negacao:
            negation = not negation
        
        if palavra in positv:
            if negation:
                negativo += intensificador
                negation = False
            else:
                positivo += intensificador
        
        elif palavra in negativ:
            if negation:
                positivo += intensificador
                negation = False
            else:
                negativo += intensificador

    if positivo > negativo:
        return 'Positivo'
    elif negativo > positivo:
        return 'Negativo'
    else:
        return 'Neutro'
