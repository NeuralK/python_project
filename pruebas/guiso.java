package pruebas;

public class guiso {
    
    public static void main(String[] args) {
        String [] albion = {"Albion online es un MMORPG sandbox de mundo abierto desarrollado por Sandbox Interactive. El juego se centra en la economía impulsada por los jugadores, la construcción de ciudades y la guerra territorial. Los jugadores pueden recolectar recursos, fabricar equipos y participar en combates PvP y PvE.", "patata", "salame", "queso", "tomate", "lechuga", "cebolla", "pimiento", "ajo", "perejil"};

        for (int i = 1; i < albion.length; i++) {
            System.out.println(albion[i]);
        }
          for (int i = 0; i < 10; i++) {
            System.out.println(albion[i]);
        }
        System.out.println(albion.length);
    }
    
}
