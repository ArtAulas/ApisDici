class Cachorro:
    def __init__(self,idade,nome):
        self.idade=idade
        self.nome=nome

    def mostra_idade(self):
        return self.idade


class Pitbull(Cachorro):
    pass

c1=Pitbull(27,"princessa")

print(c1.idade)
print(c1.nome)

print(c1.mostra_idade())

