package pruebas;

import java.util.Scanner;

public class banana {
    
    public static void main(String[] args) {
        
        int a, b = 0;

        Scanner entrada = new Scanner(System.in); // Creamos un objeto Scanner para leer la entrada del usuario

        System.out.print("Introduce un número: "); // Pedimos al usuario que introduzca un número

        a = entrada.nextInt(); // Leemos el número introducido por el usuario y lo almacenamos en la variable 'a'
        
        System.out.println("Introduce un segundo número: ");

        b = entrada.nextInt();

        if (a > b) {
            System.out.println(a + " es mayor que " + b);
        } else if (a < b) {
            System.out.println(a + " es menor que " + b);
        } 
        else{
            System.out.println(a + " es igual a " + b);
        }
    }
}
