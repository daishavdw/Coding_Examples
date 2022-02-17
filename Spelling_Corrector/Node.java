package spell;


public class Node implements INode{
    //constructor takes the letter that is making the next node.
    Node() {
        letterArray = new Node[26];
        value = 0;
        visited = false;
    }

    int value;
    Node[] letterArray;
    Boolean visited;


    @Override
    public int getValue() {
        return value;
    }

    @Override
    public void incrementValue() {
        value = value + 1;
    }

    @Override
    public INode[] getChildren() {
        return letterArray;
    }

    public boolean getBool(){
        return visited;
    }

    public void setBool(){
        visited = true;
    }

    public void setBoolFalse(){
        visited = false;
    }

}
