import java.util.Scanner;

public class PositivoNegativo {
    
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        System.out.print("Ingrese un número: ");
        int num = scanner.nextInt();

        if (num > 0) {
            System.out.println(num + " es positivo");
        } else if (num < 0) {
            System.out.println(num + " es negativo");
        } else {
            System.out.println("El número es cero");
        }
    }
}
