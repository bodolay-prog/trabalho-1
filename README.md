# trabalho-1

Trabalho de S.O sobre fork e wait

Seguindo a hipótese dada:

" A ordem em que os processos filhos são criados influencia a ordem em que eles ser ̃ao
executados e terminar ̃ao. Consequentemente, ao utilizar wait(), o processo pai tender ́a a receber
os filhos na mesma ordem em que foram criados. "

Este trabalho visa comparar o comportamento de um aplicação que faz N número de repetições para M filhos, em um espaço de 1, 2 e 4 núcleos de uma mesma CPU e guarda o tempo de execução e uma identificação para cada filho, assim podendo provar ou refutar a hipótese, por meio de um arquivo em C 'main-testet', e um arquivo .sh que faz de maneira dinâmica o teste para cada estado de número diferentes de núcleos e um arquivo em python para gerar um csv

Para execução do experimento faça:

1 - gcc -O2 -Wall -o main-tester main-tester.c, sendo:

-gcc : o compilador
-02 : parâmetro que ativa nível moderado de otimização de código para melhores resultados
-Wall : para mostrar o avisos para avisar caso exista erro
-o : gerar output "output"

2 - ./run_comparativo.sh N resultados_comparativo.log 0 0,1 0,1,2,3:

./run_comparativo.sh : sendo o arquivo bash para rodar N vezes o codígo C
"0 0,1 0,1,2,3" : sendo a configurações de núcleo que vão executadas em sequência, sendo '0' 1 núcleo, '0,1' dois núcleos, '0,1,2,3' 4 núcleos

3 - python3 analisar.py resultados_comparativo.log:

gerar um cssv usando os dados do resultados_comparativo.log

OBS: LEMBRE DE CRIAR UM CODESPACE COM 4 NÚCLEOS (4 CORE) E CASO ERRO NO CÓDIGO PYTHON USE pip install pandas scipy matplotlib numpy --break-system-packages PARA BAIXAR A BLIBLIOTECAS EXTERNAS
