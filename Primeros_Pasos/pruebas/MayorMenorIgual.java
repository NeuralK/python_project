public class MayorMenorIgual {
    public static void main(String[] args) {
        int a = 10;
        int b = 20;
        
        if (a > b) {
            System.out.println(a + " es mayor que " + b);
        }
        else if (a < b) {
            System.out.println(a + " es menor que  " + b);
    }   
        else if ( a > b || a < b) {
            System.out.println(a + " es diferente de " + b);
        } else {
            System.out.println(a + " es igual a " + b);
        }

        
    }
}
