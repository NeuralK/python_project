package juego;

public class empresas {
    public static void main(String[] args) {
        double[] distances = {23.8, 14.0, 14.0, 11.1, 27.0};
      
       for (int i = 0; i < distances.length; i++) {
            System.out.println("La distancia en la posicion " + i + " es: " + distances[i]);
        }

        double totalDistance = 0;
        for (int i = 0; i < distances.length; i++) {
            totalDistance += distances[i];
        }

        double Kiwi = distances[0];
        for (int i = 1; i < distances.length; i++) {
            if (distances[i] < Kiwi) {
                Kiwi = distances[i];
            }
        }
        System.out.println("La distancia total es: " + totalDistance);
        System.out.println("La distancia más corta es: " + Kiwi);

        int closest = 0;

        for (int i = 1; i < distances.length; i++) {
            if (distances[i] < distances[closest]) {
                closest = i;}

        }
    
    System.out.println("El índice de la distancia más corta es: " + closest);
    }      
    
}
