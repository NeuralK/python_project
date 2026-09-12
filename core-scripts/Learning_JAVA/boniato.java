public class boniato {

    public static void main(String[] args) {
       int [][] lista = {{1,2,3,4,5},{6,7,8,9,10}};

        for (int i = 0; i < lista.length; i++) {
            for (int j = 0; j < lista[i].length; j++) {
                System.out.print(lista[i][j] + " ");
            }
            System.out.println(lista[i].length);
        } 

}
}