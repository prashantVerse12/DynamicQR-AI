import { useState } from "react";
import axios from "axios";
import { QrCode } from "lucide-react";


function App() {

  const [url, setUrl] = useState("");

  const [qr, setQr] = useState(null);

  const [newUrl, setNewUrl] = useState("");

  const [analytics, setAnalytics] = useState(null);



  const createQR = async () => {

    const response = await axios.post(
      `http://127.0.0.1:8000/create-qr?content_url=${url}`
    );


    setQr(response.data);

  };



  const updateQR = async () => {

    await axios.put(
      `http://127.0.0.1:8000/update-qr/${qr.qr_id}?new_url=${newUrl}`
    );


    alert(
      "QR Updated Successfully 🚀"
    );

  };




  const getAnalytics = async () => {

    const response = await axios.get(
      `http://127.0.0.1:8000/details/${qr.qr_id}`
    );


    setAnalytics(response.data);

  };





  return (

    <div className="min-h-screen bg-gray-100 flex items-center justify-center">


      <div className="bg-white shadow-xl rounded-xl p-8 w-[550px]">


        <div className="flex gap-3 items-center mb-5">

          <QrCode size={35}/>

          <h1 className="text-3xl font-bold">

            Dynamic QR AI

          </h1>

        </div>




        <input

          className="border p-3 w-full rounded"

          placeholder="Enter URL"

          value={url}

          onChange={
            e=>setUrl(e.target.value)
          }

        />




        <button

          onClick={createQR}

          className="bg-black text-white w-full p-3 mt-4 rounded"

        >

          Generate QR

        </button>






        {

          qr && (

            <div className="text-center mt-6">


              <img

              src={qr.qr_image}

              className="w-48 mx-auto border p-2"

              />



              <p className="mt-3">

                QR ID: {qr.qr_id}

              </p>



              <a

              href={qr.qr_link}

              target="_blank"

              className="text-blue-600 underline"

              >

                Test QR

              </a>





              <hr className="my-5"/>




              <h2 className="font-bold text-xl">

                Update QR 🔄

              </h2>



              <input

              className="border p-3 w-full mt-3"

              placeholder="New destination URL"


              onChange={
                e=>setNewUrl(e.target.value)
              }

              />



              <button

              onClick={updateQR}

              className="bg-green-600 text-white p-3 w-full mt-3 rounded"

              >

              Update Same QR

              </button>





              <button

              onClick={getAnalytics}

              className="bg-blue-600 text-white p-3 w-full mt-3 rounded"

              >

              Show Analytics

              </button>






              {

              analytics && (

              <div className="mt-5">

              👁 Total Scans:

              <b>

              {analytics.scans}

              </b>


              <br />


              Active:

              {analytics.active ? " YES ✅":"NO ❌"}


              </div>


              )

              }



            </div>


          )

        }



      </div>


    </div>

  );

}


export default App;