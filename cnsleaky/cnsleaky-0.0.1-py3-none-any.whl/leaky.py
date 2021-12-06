def printit():
    print("""
    
    
    import java.io.*;
    import java.util.*;
     class Queue {
    int q[],f=0,r=0,size;
     void insert(int n) {
        Scanner in=new Scanner(System.in);
        q=new int[10];
        for(int i=0;i<n;i++) {
            System.out.print("\n Enter"+i+"element");
            int ele=in.nextInt();
            if(r+1>10) {
                System.out.println("Queue is full\nLost packet :"+ele);
                break;
            }
            else {
                r++;
                q[i]=ele;
            }
        }
    }
    void delete() {
        Scanner in=new Scanner(System.in);
        Thread t=new Thread();
        if(r==0)
            System.out.print("\nQueue is empty");
        else {
            for(int i=f;i<r;i++) {
                try {
                    t.sleep(1000);
                }
                catch(Exception e) {}
                System.out.print("\nleaked packet : "+q[i]);
                f++;
            }
        }
        System.out.println();
        
    }
    }
    class Licky extends Thread{
        public static void main(String a[])throws Exception{
            Queue q=new Queue();
            Scanner src=new Scanner(System.in);
            System.out.println("Enter the packets to be sent : ");
            int size=src.nextInt();
            q.insert(size);
            q.delete();
        }
    }

    
    
    """)


