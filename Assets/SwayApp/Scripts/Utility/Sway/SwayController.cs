using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.Events;


/*
 * author: Fredson Laguna
 * edited by: Eduardo Fisher 
 * Date: 12.1.2018
 * Edited date: 11/20/2019
 * class: SwayController
 * purpose: Will sway the object that this class is attached to. This class relies on the SwayFileReader class in order to get the necessary information needed to properly sway the object. 
*/

[DisallowMultipleComponent]
public class SwayController : MonoBehaviour
{
    private GameObject __camera;
    private Camera _camera; 
    private SwayFileReader sfr;
    private TrackerCalibrator trackerCal;
    private BertecForcePlate_Recorder bertecForcePlate;
    public bool begin;              // if true, will activate SetSpeed() method.
    public bool skipCalibration = false;
    [SerializeField]
    InputField wavetime;            // this holds the user input response for how long they want the time to be inbetween each wave stage.
    [Space]
    [SerializeField]
    private int numOfSways,       // total number of sways that will occur during current level. 
                stageNum;
    [SerializeField]
    private float speed,            // how fast to rotate towards targetSway. This is determined by targetSway and swayDuration
                                    //swayDuration,     // the amount of time it takes to rotate to targetSway and to rotate back to initial position
                  timePeriod,       // duration of the current level.
                  targetSway;       // the amount of sway (in degrees) to rotate towards 

    [SerializeField]
    private bool swaySideToSide;    // is the raft swaying side to side or forwards and backwards?

    private double currentTime;           // Both do not affect anything, used for debugging/verifying that speed variable is correct
    [SerializeField]
    [Space]
    [Header("The time it takes to complete a single sway")]
    private double completeTime;

    public float Speed { get { return speed; } }
    public float TimePeriod { get { return timePeriod; } }
    public float TargetSway { get { return targetSway; } }
    public int NumOfSways { get { return numOfSways; } }
    public int StageNum { get { return stageNum; } }
    public bool SwaySideToSide { get { return swaySideToSide; } }
    private int intWaveTime;



    private ApplicationPanel applicationPanel;
    public UnityEvent onSwayingBegins, onSwayingEnds, platePlugIn;


    // Use this for initialization
    IEnumerator Start()
    {
        _camera = GameObject.FindGameObjectWithTag("MainCamera").GetComponent<Camera>();
        wavetime = GameObject.FindGameObjectWithTag("TimeWaves").GetComponent<InputField>();
        sfr = GameObject.FindObjectOfType<SwayFileReader>();
        trackerCal = GameObject.FindObjectOfType<TrackerCalibrator>();
        applicationPanel = GameObject.FindObjectOfType<ApplicationPanel>();
        bertecForcePlate = GameObject.FindObjectOfType<BertecForcePlate_Recorder>();
        List<SwayFileReader.Stage> stages = sfr.Stages;

        intWaveTime = int.Parse(wavetime.text);

        while (true)
        {
            
            

            if (begin)
            {

                yield return sfr.ReadSwayFile();

                if(!skipCalibration)
                    yield return StartCoroutine(trackerCal.Calibrate());    // first calibrate the tracker and zero out its rotation

                foreach (SwayFileReader.Stage s in stages)
                {

                    Debug.Log("Wave Time " + intWaveTime); 
                    Debug.Log("among us " + s.ToString());

                    //Camera.main.cullingMask = LayerMask.NameToLayer("Nothing");
                    if (!s.blackScreen)
                    {
                        _camera.clearFlags = CameraClearFlags.SolidColor; //Sets black background.
                        _camera.cullingMask = 0; //This sets the render to render nothing.
                    }
                    //yield return StartCoroutine(StartWait((int)timePeriod));

                    else
                    {
                        _camera.clearFlags = CameraClearFlags.Skybox; //Sets background back to the skybox.
                        _camera.cullingMask = -1; //This sets it back to render everything.
                    }

                    if (!applicationPanel.GetPlate())//Skips force plate calibation if enabled
                    {
                        yield return StartCoroutine(bertecForcePlate.StartForcePlate());
                    }
                    else
                    {
                        if(GameObject.Find("BertecForcePlate_Recorder") != null)
                            GameObject.Find("BertecForcePlate_Recorder").SetActive(false);
                    }

                    //Debug.Log("last target sway:" + targetSway);
                    bool wasLastSwayPos = (targetSway > 0) ? false : true;
                    if (wasLastSwayPos)
                        //Debug.Log("flip next sway");

                        this.stageNum = s.stageNum;
                    this.timePeriod = s.timePeriod;
                    this.targetSway = s.sway;
                    if (wasLastSwayPos)
                        targetSway *= -1;
                    this.numOfSways = s.numOfSways;
                    this.swaySideToSide = s.swaySidetoSide;
                   
                    SetSpeed();

                    applicationPanel.UpdateSwayControllerTexts();

                    DataRecorder.Instance.AddEventInfo("SwayEvent",
                                        " stage:" + this.stageNum +
                                        " time_period:" + this.timePeriod +
                                        " sway_degree:" + this.targetSway +
                                        " #_of_sways:" + this.numOfSways);



                    onSwayingBegins.Invoke();
                    DataRecorder.Instance.BeginRecording("SwayEvent");
                    Debug.Log("start");
                    if (numOfSways > 0)
                    {
                        while (numOfSways > 0)
                        {
                            yield return StartCoroutine(Sway(targetSway));
                            targetSway *= -1;
                            numOfSways--;
                        }
                    }
                    else
                    {
                        yield return StartCoroutine(StartWait((int)timePeriod));
                    }
                    DataRecorder.Instance.FinishRecording("SwayEvent");
                    Debug.Log("end");

                    

                }//end foreach

                begin = false;
                onSwayingEnds.Invoke();

            } // end if
            else
                yield return null;
        }
    }

    /*
     * Sets sway speed
     * fields used: swayDuration, speed, targetSway, swayDuration
    */
    private void SetSpeed()
    {
        speed = timePeriod / numOfSways;
        speed = Mathf.Abs(targetSway) / speed * 2;   // targetSway is always positive to prevent negative speed. This determines how fast sway will be completed
    }


    private IEnumerator StartWait(int lenthtime)
    {
        float _lengthtime = lenthtime;
        while(_lengthtime >= 0)
        {
            _lengthtime -= Time.smoothDeltaTime;
            yield return null;
        }

        //yield return null;
    }

    /*
     * will perform one complete sway movement by using method Rot(float targetRot)
     * input: a float that determines how much an object will sway to one side
     * fields used: currentTime, completeTime
    */
    private IEnumerator Sway(float targetSway)
    {
        currentTime = Time.time;
        yield return StartCoroutine(Rot(targetSway));
        yield return StartCoroutine(Rot(0));
        completeTime = System.Math.Round(Time.time - currentTime, 2);
        //Debug.Log("Sway completion time: " + completeTime + "s");
    }

    /*
     * This method performs the actual rotation of the object.
     * It is designed so that it performs a half sway
     * input: a float that determines how much an object will be rotated
     * fields used: speed
    */
    private IEnumerator Rot(float targetRot)
    {

        if (swaySideToSide)
        {
            while (System.Math.Round(transform.eulerAngles.z, 2) != System.Math.Round(targetRot, 2) && System.Math.Round(-360 + transform.eulerAngles.z, 2) != System.Math.Round(targetRot, 2))
            {
                float anglez = Mathf.MoveTowardsAngle(transform.eulerAngles.z, targetRot, speed * Time.deltaTime);
                float angley = Mathf.MoveTowardsAngle(transform.eulerAngles.y, targetRot, speed * Time.deltaTime);
                float anglex = Mathf.MoveTowardsAngle(transform.eulerAngles.x, targetRot, speed * Time.deltaTime);
                transform.eulerAngles = new Vector3(0, 0, anglez);
                yield return null;
            }
        }
        else
        {
            while (System.Math.Round(transform.eulerAngles.x, 2) != System.Math.Round(targetRot, 2) && System.Math.Round(-360 + transform.eulerAngles.x, 2) != System.Math.Round(targetRot, 2))
            {
                float anglex = Mathf.MoveTowardsAngle(transform.eulerAngles.x, targetRot, speed * Time.deltaTime);
                float angley = Mathf.MoveTowardsAngle(transform.eulerAngles.x, targetRot, speed * Time.deltaTime);
                float anglez = Mathf.MoveTowardsAngle(transform.eulerAngles.x, targetRot, speed * Time.deltaTime);
                transform.eulerAngles = new Vector3(anglex, 0, 0);
                yield return null;
            }
        }
        //if (targetRot > 0)
        //    Debug.Log("Sway Amount: " + System.Math.Round(transform.eulerAngles.z, 2));
        //else if (targetRot < 0)
        //    Debug.Log("Sway Amount: " + System.Math.Round(-360 + transform.eulerAngles.z, 2));
    }

    /*
     * Determines the number of sways that will occur for the current stage
     * fields used: numOfSways, previousNumOfSways, timePeriod, swayDuration
    */
    //private void SetNumOfSways()
    //{
    //    numOfSways = (int)(timePeriod / swayDuration);
    //}

    public void BeginToggle(bool begin)
    {
        this.begin = begin;
    }

    public int fastParse(string number)
    {
        int result = 0;
        for (int i = 0; i < number.Length; i++)
        {
            char letter = number[i];
            result = 10 * result + (letter - 48);
        }
        return result;
    }
}
