def printit():
    print("""
    
    
    ---TCP SERVER---
    package TCPIP;
    import java.io.BufferedInputStream;
    import java.io.File;
    import java.io.FileInputStream;
    import java.io.IOException;
    import java.io.OutputStream;
    import java.net.ServerSocket;
    import java.net.Socket;
    
    public class TCP_IP {
        public final static int SOCKET_PORT = 13268;
        public final static String FILE_TO_SEND = "e:/source1.txt";
        public static void main(String []args)throws IOException
        {
            FileInputStream fis = null;
            BufferedInputStream bis=null;
            OutputStream os = null;
            ServerSocket servsock = null;
            Socket sock = null;
            try {
                servsock = new ServerSocket(SOCKET_PORT);
                while(true)
                {
                    System.out.println("Waiting....\n");
                    try
                    {
                        sock = servsock.accept();
                        System.out.println("Accepted Connection:"+sock);
                        File myFile = new File(FILE_TO_SEND);
                        byte[] mybytearray = new byte[(int)myFile.length()];
                        fis = new FileInputStream(myFile);
                        bis=new BufferedInputStream(fis);
                        bis.read(mybytearray,0,mybytearray.length);
                        os=sock.getOutputStream();
                        System.out.println("Sending " +FILE_TO_SEND+ "(" +mybytearray.length+ " bytes");
                        os.write(mybytearray, 0, mybytearray.length);
                        os.flush();
                        System.out.println("Done.");
                    }
                    finally {
                        if(bis!=null) bis.close();
                        if(os!=null) os.close();
                        if(sock!=null) sock.close();
                    }
                }
            }
            finally {
                if(servsock!=null) servsock.close();
                    }
                }
                
    }
            
            
        
    ----TCP----
    package TCPIP;
    import java.io.BufferedOutputStream;
    import java.io.FileOutputStream;
    import java.io.InputStream;
    import java.io.IOException;
    import java.net.Socket;
    
    public class TCP_IP_Client {
    public final static int SOCKET_PORT = 13268;
    public final static String SERVER = "127.0.0.1";
    public final static String FILE_TO_RECEIVE = "e:/source-downloaded.txt";
    public final static int FILE_SIZE = 6022386;
    public static void main(String args[])throws IOException
    {
        int bytesRead;
        int current=0;
        FileOutputStream fos=null;
        BufferedOutputStream bos=null;
        Socket sock = null;
        try
        {
            sock=new Socket(SERVER,SOCKET_PORT);
            System.out.println("Connecting...");
            byte[] mybytearray = new byte[FILE_SIZE];
            InputStream is =sock.getInputStream();
            fos = new FileOutputStream(FILE_TO_RECEIVE);
            bos = new BufferedOutputStream(fos);
            bytesRead = is.read(mybytearray,0,mybytearray.length);
            current=bytesRead;
            do {
                bytesRead=is.read(mybytearray,current,(mybytearray.length-current));
                if(bytesRead>=0) current+=bytesRead;
            }while(bytesRead>-1);
            bos.write(mybytearray,0,current);
            bos.flush();
            System.out.println("File " +FILE_TO_RECEIVE+ " downloaded("+current+"bytes read)");
        }
        finally {
            if(fos!=null) fos.close();
            if(bos!=null) bos.close();
            if(sock!=null) sock.close();
        }
    }
    }

    
    """)


