using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.Events;

//writing
using System.IO;
using UnityEditor;
//

//Edited by: Michael Fang 
//https://blogs.oregonstate.edu/anima/2016/08/02/unity3d-5-x-make-quick-scrolling-text-field/

//Edited date: 10/12/2022

public class CreationPanel : MonoBehaviour
{
    [SerializeField]
    Text stageNum;

    [SerializeField]
    InputField waveDurration, rotation, swayTotal;

    private string path;
    private int sway;
    private bool gameStart;
    private int stagenum;
    private int black;



    // Start is called before the first frame update
    void Start()
    {
        waveDurration = GameObject.FindGameObjectWithTag("NextTimePeriod").GetComponent<InputField>();
        rotation = GameObject.FindGameObjectWithTag("NextTargetSway").GetComponent<InputField>();
        swayTotal = GameObject.FindGameObjectWithTag("NextNumOfSways").GetComponent<InputField>();

        path = Application.streamingAssetsPath + "/Sway_Files/Sway.txt";
        sway = 0;
        gameStart = false;
        stagenum = GetLastLine() + 1;
        black = 0;

    }

    // Update is called once per frame
    void Update()
    {
        GameObject.FindGameObjectWithTag("NextStage").GetComponent<Text>().text = stagenum.ToString();
        GameObject.FindGameObjectWithTag("FileText").GetComponent<Text>().text = GetFileText();
    }

    public void UpdateWaveInput(string text)
    {
        this.waveDurration.text = text;
    }
    public void UpdateRotationInput(string text)
    {
        this.rotation.text = text;
    }
    public void UpdateSwayInput(string text)
    {
        this.swayTotal.text = text;
    }
    public void UpdateWaveInput(int amount)
    {
        UpdateWaveInput(amount.ToString());
    }
    public void UpdateRotationInput(int amount)
    {
        UpdateRotationInput(amount.ToString());
    }
    public void UpdateSwayInput(int amount)
    {
        UpdateSwayInput(amount.ToString());
    }

    public void ToggleSway()
    {//find a better implementation
        sway = (sway - 1) * -1;
    }
    public void ToggleBlack()
    {//find a better implementation
        black = (black - 1) * -1;
    }

    public int GetLastLine()
    {
        int lineCounter = 0;
        StreamReader reader = new StreamReader(path);
        ArrayList lineList = new ArrayList();

        while (reader.Peek() != -1)
        {
            lineList.Add(reader.ReadLine());
            lineCounter++;
        }
        reader.Close();
        /*
        foreach (var item in lineList)
        {
            lineounter++;
            //Debug.Log(item);
        }
        */

        Debug.Log(lineList[lineCounter - 1]);


        //get first number by getting string before first comma
        string lastLine = lineList[lineCounter - 1].ToString();
        char[] lastLineArray = lastLine.ToCharArray();
        int linePostion = 1;

        for (int i = 0; i < lastLine.Length; i++)
        {
            if (lastLineArray[i] == ',')
            {
                linePostion = i;
                break;
            }
        }

        Debug.Log(lineList[lineCounter - 1].ToString().Substring(0, linePostion));
        return int.Parse(lineList[lineCounter - 1].ToString().Substring(0, linePostion));

    }

    public void AddLine()
    {
        if (!gameStart)
        {
            //
            string message = stagenum + ", " + waveDurration.text + ", " + rotation.text + ", " + swayTotal.text + ", " + sway + ", " + black;
            //

            StreamWriter writer = new StreamWriter(path, true);
            writer.WriteLine(message);
            writer.Close();

            stagenum++;
        }

    }

    public void DeleteLine()
    {
        if (!gameStart)
        {
            int lineCounter = 0;
            StreamReader reader = new StreamReader(path);
            ArrayList lineList = new ArrayList();

            while (reader.Peek() != -1)
            {
                lineList.Add(reader.ReadLine());
                lineCounter++;
            }

            reader.Close();
            string message = "";
            StreamWriter deleter = new StreamWriter(path, false);

            for (int i = 0; i < lineCounter - 1; i++)
            {
                message = lineList[i].ToString();
                deleter.WriteLine(message);
            }
            deleter.Close();

            stagenum--;
        }


        /*
        string message = stagenum + ", " + waveDurration.text + ", " + rotation.text + ", " + swayTotal.text + ", " + sway;
        //

        StreamWriter writer = new StreamWriter(path, true);
        writer.WriteLine(message);
        writer.Close();

        stagenum++;
        */
    }

    public string GetFileText()
    {
        StreamReader reader = new StreamReader(path);
        string message = "";

        while (reader.Peek() != -1)
        {
            message += reader.ReadLine();
            if (reader.Peek() != -1)
            {
                message += "\n";
            }
        }

        reader.Close();
        return message;
    }

    public void StartGame()
    {
        gameStart = true;
    }

    public void EndGame()
    {
        gameStart = false;
    }

}
