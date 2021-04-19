all: prog2_gbn

prog2: prog2_gbn.o 
	gcc -Wall prog2_gbn.o -o prog2_gbn

prog2.o: prog2_gbn.c
	gcc -c prog2_gbn.c

clean:
	rm -rf *.o prog2_gbn
