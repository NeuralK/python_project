package pruebas;
import java.util.Scanner;
public class kiwi {
    public static void main(String[] args) {
    
    int a = 0;
    int b = 18;
        while (true){
        System.out.println("quiero queque");
         
        Scanner entrada = new Scanner(System.in); // Creamos un objeto Scanner para leer la entrada del usuario

        System.out.print("Introduce tu edad: "); // Pedimos al usuario que introduzca un número

        a = entrada.nextInt(); // Leemos el número introducido por el usuario y lo almacenamos en la variable 'a'

        if (a >= b) {
            System.out.println(" Es mayor a " + b + " años");
        
        } 
     
       
        else
        {
            System.out.println("Raja de aca nene");
        }
    
    }
}
}

