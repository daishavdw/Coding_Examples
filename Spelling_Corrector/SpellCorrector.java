package spell;

import java.io.File;
import java.io.IOException;
import java.util.*;

public class SpellCorrector implements ISpellCorrector {
    Trie trie = new Trie();

    @Override
    //Reads in all the words from an input file and stores them in a Trie object
    public void useDictionary(String dictionaryFileName) throws IOException {
        File inputFile = new File(dictionaryFileName);
        Scanner scanner = new Scanner(inputFile);
        scanner.useDelimiter("((#[^\\n]*\\n)|(\\s+))+");

        while (scanner.hasNext()) {
            String str = scanner.next();
            trie.add(str.toLowerCase());
        }
    }

    @Override
    //Will take a misspelled input word and suggest a word
    public String suggestSimilarWord(String inputWord) {
        System.out.println("Input is " + inputWord);
        inputWord = inputWord.toLowerCase();
        if (trie.find(inputWord) == null) { //check if word exists in dictionary already.
            Vector<String> Candidates1 = new Vector<String>();
            TreeSet<String> FinalWords; //take part of this out?
            Vector<String> Candidates2;
            RunTests(inputWord, Candidates1);

            FinalWords = DictionaryCheck(Candidates1); //checking all the candidates against the dictionary
            String returnWord = CandidateSearch(FinalWords); //using above words/size to determine next step

            if (returnWord == null){ //2 edit distance
                System.out.println("Going into the 2nd distance edits");
                Candidates2 = SecondRun(Candidates1);
                FinalWords = DictionaryCheck(Candidates2);
                returnWord = CandidateSearch(FinalWords);
            }

            //System.out.println("Word is: " + returnWord); //when 1 word is returned
            return returnWord;
        }
        //System.out.println("Was already in the dictionary");
        return inputWord;
    }

    public TreeSet<String> DictionaryCheck(Vector<String> Candidates){ //checks if word is in dictionary
        //Iterate thru candidates. Keep track of matches
        TreeSet<String> FinalWords = new TreeSet<>();
        for (int index = 0; index < Candidates.size(); index++) {
            String currentWord = Candidates.get(index);
            //System.out.println(currentWord);
            if (trie.find(currentWord) != null) {
                System.out.println("Found " + currentWord + " in the dictionary");
                FinalWords.add(currentWord);
            }
        }
        return FinalWords;
    }

    public String CandidateSearch(TreeSet<String> FinalWords){ //returns words depending on what was found
        if (FinalWords.size() > 1) { //deal with multiple candidates found in dictionary
            System.out.println("Size is " + FinalWords.size() + ". Printing the candidates:");//remove later
            System.out.println(FinalWords.toString());//remove later
            return MultiWords(FinalWords);

        }
        else if (FinalWords.size() == 0) { //none of the first candidate words found in the dictionary.
            System.out.println("no matches");
            return null;
        }
        else { // only one of the candidate words was found in the dictionary
            //System.out.println("Lone candidate in the dictionary");
            return FinalWords.first();}
    }

    public Vector<String> SecondRun(Vector<String>Candidates1) {
        Vector<String> Candidates2 = new Vector<String>();
        String currentWord;
        for (int index = 0; index < Candidates1.size(); index++) {
           currentWord = Candidates1.get(index);
           RunTests(currentWord, Candidates2);
        }
        return Candidates2;
    }

    //If we have multiple candidate words, pick the one that shows up in the trie more times
    public String MultiWords(TreeSet<String> FinalWords) {
        System.out.println("Working in multiword function:");
        int highestcount = 0;
        String highestWord = FinalWords.first();
        for (String currentword : FinalWords){
            if(trie.returnFreq(currentword) > highestcount){
                highestcount = trie.returnFreq(currentword);
                highestWord = currentword;
            }
        }
        return highestWord;
    }

    //Looking for candidate words based on how the misspelling could have occured.
    public void RunTests(String inputWord, Vector<String>TheTree){
        Deletions(inputWord, TheTree);
        Transposition(inputWord, TheTree);
        Alteration(inputWord, TheTree);
        Insertion(inputWord, TheTree);
    }

    //Considering words where a letter was deleted
    public void Deletions(String word, Vector<String>Candidates) {
        for(int index = 0; index < word.length(); index++){
            StringBuilder StringHolder = new StringBuilder();
            StringHolder.append(word);
            StringHolder.deleteCharAt(index);
            //System.out.println("New cand. is " + StringHolder.toString());
            Candidates.add(StringHolder.substring(0));

        }
    }

    //Considering words where two letters were transposed
    public void Transposition(String word, Vector<String>Candidates) {
        for(int index = 0; index < word.length() -1; index++) {
           char chars[] = word.toCharArray();
           char temp = chars[index];
           chars[index] = chars[index + 1];
           chars[index + 1] = temp;
           String newWord = new String(chars);
           //System.out.println("New canidate: " + newWord);
           Candidates.add(newWord);
        }
    }

    //Considering words where one letter was entered incorrectly
    public void Alteration(String word, Vector<String>Candidates) {
        for(int index = 0; index < word.length(); index++){
            char ignore = word.charAt(index);
            for(char c = 'a'; c <= 'z'; c++) {
                if(c != ignore) {
                    StringBuilder StringHolder = new StringBuilder();
                    StringHolder.append(word);
                    StringHolder.insert(index, c);
                    StringHolder.deleteCharAt(index + 1);
                    //System.out.println("New cand. is " + StringHolder.toString());
                    Candidates.add(StringHolder.substring(0));
                }
            }
        }

    }

    //Considering words were there as an extra letter inserted
    public void Insertion(String word, Vector<String>Candidates) {
        for(int index = 0; index < word.length() + 1; index++){
            for(char c = 'a'; c <= 'z'; c++) {
                StringBuilder StringHolder = new StringBuilder();
                StringHolder.append(word);
                StringHolder.insert(index, c);
                //System.out.println("New cand. is " + StringHolder.toString());
                Candidates.add(StringHolder.substring(0));

            }
        }
    }
}
