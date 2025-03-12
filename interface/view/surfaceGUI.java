// package view;

// import java.awt.*;
// import java.awt.event.*;

// import javax.swing.*;

// public class surfaceGUI extends JFrame {
//     public surfaceGUI() {
//         initComponents();
//     }

//     private void initComponents() {

//         contentPane = new JPanel();
//         runLabel = new JLabel();
//         runButton = new JLabel();
//         topSep = new JSeparator();
//         midSep = new JSeparator();
//         topScroll = new JScrollPane();
//         userArea = new JTextArea();
//         bottomScroll = new JScrollPane();
//         errorArea = new JTextArea();
//         bottomSep = new JSeparator();
//         slogalLabel = new JLabel();
//         menuBar = new JMenuBar();
//         starLogo = new JLabel();
//         fileMenu = new JMenu();
//         newFileItem = new JMenuItem();
//         openFileItem = new JMenuItem();
//         saveFileItem = new JMenuItem();
//         helpMenu = new JMenu();
//         settingsMenu = new JMenu();

//         setDefaultCloseOperation(WindowConstants.EXIT_ON_CLOSE);
//         setBackground(new Color(36, 27, 53));
//         setCursor(new Cursor(Cursor.DEFAULT_CURSOR));
//         setName("frame"); // NOI18N
//         setPreferredSize(new Dimension(800, 550));

//         contentPane.setBackground(new Color(36, 27, 53));
//         contentPane.setBorder(BorderFactory.createEmptyBorder(1, 1, 1, 1));
//         contentPane.setForeground(new Color(255, 255, 255));

//         starLogo.setIcon(new ImageIcon(getClass().getResource("/assets/star.png"))); // NOI18N

//         runLabel.setFont(new Font("Times New Roman", 0, 12)); // NOI18N
//         runLabel.setForeground(new Color(255, 255, 255));
//         runLabel.setHorizontalAlignment(SwingConstants.CENTER);
//         runLabel.setText("RUN");

//         runButton.setIcon(new ImageIcon(getClass().getResource("/assets/run.png"))); // NOI18N
//         runButton.addMouseListener(new MouseAdapter() {
//             public void mouseClicked(MouseEvent evt) {
//                 runButtonMouseClicked(evt);
//             }
//         });

//         topScroll.setBorder(null);

//         userArea.setBackground(new Color(48, 41, 63));
//         userArea.setColumns(20);
//         userArea.setFont(new Font("Times New Roman", 0, 12)); // NOI18N
//         userArea.setForeground(new Color(255, 255, 255));
//         userArea.setRows(5);
//         userArea.setText("[ Please Type Here ]");
//         userArea.setBorder(null);
//         userArea.addFocusListener(new FocusAdapter() {
//             public void focusGained(FocusEvent evt) {
//                 userAreaFocusGained(evt);
//             }
//             public void focusLost(FocusEvent evt) {
//                 userAreaFocusLost(evt);
//             }
//         });
//         topScroll.setViewportView(userArea);

//         bottomScroll.setBorder(null);

//         errorArea.setEditable(false);
//         errorArea.setBackground(new Color(48, 41, 63));
//         errorArea.setColumns(20);
//         errorArea.setFont(new Font("Times New Roman", 0, 12)); // NOI18N
//         errorArea.setForeground(new Color(255, 255, 255));
//         errorArea.setRows(5);
//         errorArea.setText("[ Error Messages ]");
//         errorArea.setBorder(null);
//         bottomScroll.setViewportView(errorArea);

//         slogalLabel.setFont(new Font("Times New Roman", 1, 12)); // NOI18N
//         slogalLabel.setForeground(new Color(255, 255, 255));
//         slogalLabel.setText("APBL - Booking Made Easy");

//         GroupLayout contentPaneLayout = new GroupLayout(contentPane);
//         contentPane.setLayout(contentPaneLayout);
//         contentPaneLayout.setHorizontalGroup(
//             contentPaneLayout.createParallelGroup(GroupLayout.Alignment.LEADING)
//             .addGroup(GroupLayout.Alignment.TRAILING, contentPaneLayout.createSequentialGroup()
//                 .addContainerGap(331, Short.MAX_VALUE)
//                 .addComponent(slogalLabel)
//                 .addGap(324, 324, 324))
//             .addComponent(topSep)
//             .addComponent(bottomSep, GroupLayout.Alignment.TRAILING)
//             .addComponent(midSep)
//             .addComponent(bottomScroll)
//             .addGroup(contentPaneLayout.createSequentialGroup()
//                 .addContainerGap()
//                 .addComponent(starLogo)
//                 .addPreferredGap(LayoutStyle.ComponentPlacement.RELATED, GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
//                 .addComponent(runLabel, GroupLayout.PREFERRED_SIZE, 40, GroupLayout.PREFERRED_SIZE)
//                 .addPreferredGap(LayoutStyle.ComponentPlacement.RELATED)
//                 .addComponent(runButton)
//                 .addGap(36, 36, 36))
//             .addComponent(topScroll)
//         );
//         contentPaneLayout.setVerticalGroup(
//             contentPaneLayout.createParallelGroup(GroupLayout.Alignment.LEADING)
//             .addGroup(GroupLayout.Alignment.TRAILING, contentPaneLayout.createSequentialGroup()
//                 .addContainerGap()
//                 .addGroup(contentPaneLayout.createParallelGroup(GroupLayout.Alignment.TRAILING)
//                     .addGroup(contentPaneLayout.createSequentialGroup()
//                         .addComponent(runButton)
//                         .addGap(3, 3, 3))
//                     .addGroup(contentPaneLayout.createSequentialGroup()
//                         .addComponent(runLabel)
//                         .addGap(5, 5, 5))
//                     .addGroup(contentPaneLayout.createSequentialGroup()
//                         .addComponent(starLogo)
//                         .addGap(3, 3, 3)))
//                 .addComponent(topSep, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE)
//                 .addGap(0, 0, 0)
//                 .addComponent(topScroll, GroupLayout.DEFAULT_SIZE, 207, Short.MAX_VALUE)
//                 .addGap(0, 0, 0)
//                 .addComponent(midSep, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE)
//                 .addGap(0, 0, 0)
//                 .addComponent(bottomScroll, GroupLayout.PREFERRED_SIZE, 216, GroupLayout.PREFERRED_SIZE)
//                 .addGap(0, 0, 0)
//                 .addComponent(bottomSep, GroupLayout.PREFERRED_SIZE, 10, GroupLayout.PREFERRED_SIZE)
//                 .addPreferredGap(LayoutStyle.ComponentPlacement.RELATED)
//                 .addComponent(slogalLabel)
//                 .addGap(15, 15, 15))
//         );

//         menuBar.setBackground(new Color(36, 27, 53));
//         menuBar.setBorder(BorderFactory.createEmptyBorder(1, 1, 1, 1));

//         fileMenu.setForeground(new Color(255, 255, 255));
//         fileMenu.setText("File");

//         newFileItem.setText("New File...");
//         fileMenu.add(newFileItem);

//         openFileItem.setText("Open File...");
//         fileMenu.add(openFileItem);

//         saveFileItem.setText("Save");
//         fileMenu.add(saveFileItem);

//         menuBar.add(fileMenu);

//         helpMenu.setForeground(new Color(255, 255, 255));
//         helpMenu.setText("Help");
//         menuBar.add(helpMenu);
        
//         settingsMenu.setForeground(new Color(255, 255, 255));
//         settingsMenu.setText("Settings");
//         menuBar.add(settingsMenu);

//         setJMenuBar(menuBar);

//         GroupLayout layout = new GroupLayout(getContentPane());
//         getContentPane().setLayout(layout);
//         layout.setHorizontalGroup(
//             layout.createParallelGroup(GroupLayout.Alignment.LEADING)
//             .addComponent(contentPane, GroupLayout.DEFAULT_SIZE, GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
//         );
//         layout.setVerticalGroup(
//             layout.createParallelGroup(GroupLayout.Alignment.LEADING)
//             .addComponent(contentPane, GroupLayout.DEFAULT_SIZE, GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
//         );

//         pack();
//         setLocationRelativeTo(null);
//     }// </editor-fold>

//     private void userAreaFocusGained(FocusEvent evt) {
//         if (userArea.getText().equals("[ Please Type Here ]")) {
//             userArea.setText("");
//         }
//     }

//     private void userAreaFocusLost(FocusEvent evt) {
//         if (userArea.getText().equals("")) {
//             userArea.setText("[ Please Type Here ]");
//         }
//     }

//     private void runButtonMouseClicked(MouseEvent evt) {
//         if ((userArea.getText().equals("[ Please Type Here ]")) || userArea.getText().equals("")) {
//             System.out.println("Please enter valid input!");
//         } else {
//             // TODO add your handling code here:
//         }
//     }

//     public static void main(String args[]) {
//         EventQueue.invokeLater(new Runnable() {
//             public void run() {
//                 new surfaceGUI().setVisible(true);
//             }
//         });
//     }

//         // Variables declaration - do not modify                     
//         private JScrollPane bottomScroll;
//         private JSeparator bottomSep;
//         private JPanel contentPane;
//         private JTextArea errorArea;
//         private JMenu fileMenu;
//         private JMenu helpMenu;
//         private JMenuBar menuBar;
//         private JSeparator midSep;
//         private JMenuItem newFileItem;
//         private JMenuItem openFileItem;
//         private JLabel runButton;
//         private JLabel runLabel;
//         private JMenuItem saveFileItem;
//         private JMenu settingsMenu;
//         private JLabel slogalLabel;
//         private JLabel starLogo;
//         private JScrollPane topScroll;
//         private JSeparator topSep;
//         private JTextArea userArea;
//         // End of variables declaration 
// }