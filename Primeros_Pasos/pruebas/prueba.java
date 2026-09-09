package pruebas;
import java.util.Random;
public class prueba{
    public static void main(String[] args) {

        Random azar = new Random();
        
        int dado;
        
        dado = 1 + azar.nextInt(12);
        if (dado == 5){
            System.out.println(dado + " != 2");
        }
        System.out.println(dado);
        
       
        int pepe;

        pepe = 1 + azar.nextInt(12);

        System.out.println(pepe);
    }}