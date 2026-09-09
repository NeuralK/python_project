package juego;

public class calificaciones {
    public static void main(String[] args) {
        int[] calificaciones = new int[3];
        calificaciones[0] = 7;
        calificaciones[1] = 6;
        calificaciones[2] = 1;

        System.out.println("La calificacion en la posicion 3 es: " + calificaciones[2]);
        System.out.println("El numero total de calificaciones es: " + calificaciones.length);
        System.out.println("El promedio de las calificaciones es: " + (calificaciones[0] + calificaciones[1] + calificaciones[2]) / 3);

        for (int i = 0; i <= 2; i++) {
            System.out.println(calificaciones[i]);
        }
        int papa = 0;
        for (int i = 0; i < calificaciones.length; i++) {
           papa += calificaciones[i];
        }
         System.out.println("El promedio de las calificaciones es: " + (papa / calificaciones.length));

        
        }
    }
