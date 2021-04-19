all: prog2_abp

prog2: prog2_abp.o 
	gcc -Wall prog2_abp.o -o prog2_abp

prog2.o: prog2_abp.c
	gcc -c prog2_abp.c

clean:
	rm -rf *.o prog2_abp
