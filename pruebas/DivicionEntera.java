import java.util.Scanner;
public class DivicionEntera {
    public static void main(String[] args) {

        Scanner in = new Scanner(System.in);
        System.out.print("Ingrese el primer número: ");
        int a = in.nextInt();
        System.out.print("Ingrese el segundo número: ");
        int b = in.nextInt();

        int resultado = a / b;
        System.out.println("El resultado de la división entera de " + a + " entre " + b + " es: " + resultado);
    }


    }

