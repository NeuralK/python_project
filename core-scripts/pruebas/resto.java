import java.util.Scanner;

public class resto {
    public static void main(String[] args) {
        
        Scanner scanner = new Scanner(System.in);
        System.out.print("Ingrese un número: ");
        int num = scanner.nextInt();

      if (num % 2 == 0) {
          System.out.println(num + " es par");
      } else {
          System.out.println(num + " es impar");
      }
    }
}