public class Main {
    public static void main(String[] args) {

        class node {
            protected Integer dataNode;
            protected node ptr;

            public node() {
                dataNode = null;
                ptr = null;
            }

            public node(Integer d, node e) {
                dataNode = d;
                ptr = e;
            }

            public void setData(Integer d) {
                dataNode = d;
            }

            public void setPtg(node e) {
                ptr = e;
            }

            public Integer getData() {
                return dataNode;
            }

            public node getPtr() {
                return ptr;
            }
        }

        class tumpukanGG {
            private node tumpukanGanjil;
            private node tumpukanGenap;

            public tumpukanGG() {
                tumpukanGanjil = null;
                tumpukanGenap = null;
            }

            public void push(int data) {
                if (data % 2 == 0) { // Data genap
                    tumpukanGenap = new node(data, tumpukanGenap);
                } else { // Data ganjil
                    tumpukanGanjil = new node(data, tumpukanGanjil);
                }
            }

            public Integer popganjil() {
                if (tumpukanGanjil == null) {
                    System.out.println("Tumpukan ganjil kosong");
                    return null;
                }
                Integer data = tumpukanGanjil.getData();
                tumpukanGanjil = tumpukanGanjil.getPtr();
                return data;
            }

            public Integer popgenap() {
                if (tumpukanGenap == null) {
                    System.out.println("Tumpukan genap kosong");
                    return null;
                }
                Integer data = tumpukanGenap.getData();
                tumpukanGenap = tumpukanGenap.getPtr();
                return data;
            }

            public void cetakganjil() {
                node current = tumpukanGanjil;
                System.out.print("Tumpukan Ganjil: ");
                while (current != null) {
                    System.out.print(current.getData() + " ");
                    current = current.getPtr();
                }
                System.out.println();
            }

            public void cetakgenap() {
                node current = tumpukanGenap;
                System.out.print("Tumpukan Genap: ");
                while (current != null) {
                    System.out.print(current.getData() + " ");
                    current = current.getPtr();
                }
                System.out.println();
            }
        }


        tumpukanGG a = new tumpukanGG();

        a.push(5);
        a.push(9);
        a.push(10);
        a.push(13);
        a.push(20);
        a.cetakganjil();;
        a.cetakgenap();

        System.out.println("Pop Ganjil: " + a.popganjil());
        System.out.println("Pop Genap: " + a.popgenap());

        a.cetakganjil();
        a.cetakgenap();
    }
}
