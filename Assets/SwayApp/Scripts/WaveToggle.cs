using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.Events;

public class WaveToggle : MonoBehaviour
{
    public Rigidbody rb;
    public GameObject ocean;
    void FreezeConstraints()
    {
        rb.constraints = RigidbodyConstraints.FreezePositionY;
        rb.position = new Vector3(0, 10.1f, 0);
        ocean.active = false;
    }

    void UnFreezeConstraints()
    {
        rb.constraints = RigidbodyConstraints.None;
        ocean.active = true;
    }

    public void onToggle(bool selected)
    {
        if (selected == true)
            FreezeConstraints();
        else
            UnFreezeConstraints();
    }
}
