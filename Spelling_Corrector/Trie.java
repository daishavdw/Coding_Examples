package spell;

import java.lang.*;

public class Trie implements ITrie {
    int wordCount = 0;
    int nodeCount = 1;
    Node root = new Node();
    Node currentNode;
    int index = 0;

    @Override
    //adding a word into our Trie
    public void add(String word) {
        currentNode = root;

        //System.out.println("Adding " + word);
        for (int i = 0; i < word.length(); ++i) {
            char letter = word.charAt(i);
            index = letter - 'a';

            if (currentNode.getChildren()[index] == null) { //adding new node and children
                newNode(letter);
            } else { //Not null and just keep looping
                currentNode = (Node) currentNode.getChildren()[index];
            }
        }

        if (currentNode.getValue() == 0) { //keeping track of the number of unique words that we have
            wordCount = wordCount + 1;
        }
        currentNode.incrementValue(); //incrementing the word value on the last node
    }

    //creating a new node
    public void newNode(char let) { //don't need the char, just using for testing
        currentNode.getChildren()[index] = new Node();
        currentNode = (Node) currentNode.getChildren()[index];
        nodeCount = nodeCount + 1;
        //System.out.println("children: " + currentNode.getChildren().length);
    }

    @Override
    //Used to check if our Trie contains a specific word
    public INode find(String word) {
        Node MyNode = root;
        for (int i = 0; i < word.length(); ++i) {
            char letter = word.charAt(i);
            index = letter - 'a';

            if (MyNode.getChildren()[index] == null) {
                return null;
            } else {
                MyNode = (Node) MyNode.getChildren()[index];
            }
        }
        if (MyNode.getValue() != 0) {
            return MyNode;
        }
        //System.out.println("word was not found");
        return null;
    }

    @Override
    //printing the wordcount
    public int getWordCount() {
        return wordCount;
    }

    @Override
    //printing the number of nodes we have
    public int getNodeCount() {
        return nodeCount;
    }

    //creating hashCode
    public int hashCode() {
        int numCode;

        if (root.getChildren() != null) {
            for (int i = 0; i < 26; i++) {
                //as you hit non null, use that. Have a case for an empty trie
                if (root.getChildren()[i] != null) {
                    numCode = (i) * wordCount * nodeCount;
                    return numCode;
                }
            }
        }
        return 0;
    }

    //printing everything in alphabetical order
    public String toString() {
        StringBuilder FinalStrings = new StringBuilder();
        StringBuilder currentString = new StringBuilder();
        FinalStrings = treeLoop(root, currentString, FinalStrings);

        System.out.println(wordCount + " words should print out: ");
        System.out.println(FinalStrings.toString());
        System.out.println("Done!");

        return FinalStrings.toString();
    }

    //Helping us to assemble different nodes into printed out words.
    public StringBuilder treeLoop(Node ThisNode, StringBuilder currentString, StringBuilder FinalStrings) { // Recursive part of toString
        for (int i = 0; i < 26 ; i++) {
            if (ThisNode.getChildren()[i] != null) {
                Node TempNode = (Node) ThisNode.getChildren()[i];
                char letter = (char) ('a' + i);
                currentString.append(letter);
                if (TempNode.getValue() > 0) {
                    FinalStrings.append(currentString.substring(0) + "\n");
                }
                treeLoop((Node)ThisNode.getChildren()[i], currentString, FinalStrings);
                currentString.delete(currentString.length()-1, currentString.length());
            }
        }

        return FinalStrings;
    }

    public Node returnRoot() {
        return root;
    }

    //Checking if two Trie objects are identical or not.
    public boolean equals(Object Trie2) {
        //If the object is empty, return false
        if (Trie2 == null){
            return false;
        }

        if (Trie2 instanceof Trie != true) { //if wrong type of object, return false
            return false;
        }

        Node ThisNode = root;
        Node ThisNode2 = ((Trie) Trie2).returnRoot();
        if (wordCount != ((Trie) Trie2).getWordCount()) { //if Trie1 and Trie2 don't have same word count, they aren't the same
            // System.out.println("Word count not the same");
            return false;
        }
        if (nodeCount != ((Trie) Trie2).getNodeCount()) { //if number of nodes isn't the same, also not the same
            // System.out.println("Node count not the same");
            return false;
        }
         if (equalsBool(ThisNode, ThisNode2) == false) { //checking if all the nodes between the two Trie objects are the same
             System.out.println("was found false");
             return false;
         }

         System.out.println("Found equal");
         return true;
    }

    //checking if two nodes are equal
    public boolean equalsBool(Node Node1, Node Node2) {
        //if one of the nodes is null, we know that Node1 and Node2 cannot be equal
        for (int num = 0; num < 26; num++) {
            if (Node1.getChildren()[num] != null && Node2.getChildren()[num] == null) {
                return false;
            }
            if (Node1.getChildren()[num] == null && Node2.getChildren()[num] != null) {
                return false;
            }

            if (Node1.getValue() != Node2.getValue()) { //if the two nodes are not the same
                System.out.println("Unequel! The values of " + num + " came back as: " + Node1.getValue() + " and " + Node2.getValue());
                return false;
                }

            if (Node1.getChildren()[num] != null && Node2.getChildren()[num] != null) { //checking children nodes
                    if (equalsBool((Node) Node1.getChildren()[num], (Node) Node2.getChildren()[num]) == false){
                        return false;
                    }
            }
        }
            return true; //nodes were equal
    }

    //checking the number of frequencies of a specific word.
    public int returnFreq(String word) {
        Node MyNode = root;
        //System.out.println("Using the find function");
        for (int i = 0; i < word.length(); ++i) {
            char letter = word.charAt(i);
            index = letter - 'a';

            //checking if the root node has any children
            if (MyNode.getChildren()[index] == null) {
                //System.out.println(letter + " is not found ");
                return 0;
            } else {
                MyNode = (Node) MyNode.getChildren()[index];
                //System.out.println(letter + " is found");
            }
        }
        if (MyNode.getValue() != 0) { //returning the found word
            return MyNode.getValue();
        }
        //System.out.println("word was not found");
        return 0; //did not find the word we were searching for
    }
}
