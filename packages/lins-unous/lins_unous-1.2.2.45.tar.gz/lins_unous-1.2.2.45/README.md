# lins-unous #

Pacote para ser utilizado na integração Unous.

## Variaveis de Ambiente necessarias

> ### MINDSET_USER    
>> Parametro necessário para token da UNOUS
 
> ### MINDSET_PASS     
>> Parametro necessário para token da UNOUS 

> ### MINDSET_URL   
>> URL UNOUS

> ### MINDSET_NOTIFY_URL
>> Url para notificação de termino das integrações ao sistema Mindset

## Integracoes

> ### Produtos
>> Basta instanciar a classe ApiUnous e chamar o metodo integrar_produtos passando a lista de produtos

> ### Produtos Tamanhos 
>> Basta instanciar a classe ApiUnous e chamar o metodo integrar_produtos_tamanhos passando a lista de produtos tamanhos

> ### Integrar fornecedores
>> Basta instanciar a classe ApiUnous e chamar o metodo integrar_fornecedores passando a lista de fornecedores

> ### Integrar pedidos
>> Basta instanciar a classe ApiUnous e chamar o metodo integrar_pedidos passando a lista de pedidos

> ### Integrar lojas
>> Basta instanciar a classe ApiUnous e chamar o metodo integrar_lojas passando a lista de lojas

> ### Integrar lojas informacoes
>> Basta instanciar a classe ApiUnous e chamar o metodo integrar_lojas_info passando a lista de lojas informações

> ### Integrar metricas
>> Basta instanciar a classe ApiUnous e chamar o metodo integrar metricas passando a lista de metricas

> ### Notificar
>> Ao ser chamado notifica o sistema Mindset que as integrações terminaram e que pode começar o cálculo do planejamento de compras 