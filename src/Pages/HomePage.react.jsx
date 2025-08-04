import React, { useState, useEffect }  from 'react';
import './HomePage.css'
import MacroHistoryChart from './MacroHistoryChart.react'; 

function HomePage({token, logout}) {
    // const localLast = 'http://localhost:5055/api/last-macros'
    // const localGenerate = 'http://localhost:5055/api/generate'
    // const localAddMacro = 'http://localhost:5055/api/add-macro'

    const prodLast = 'https://calorie-tracker-xr.up.railway.app/api/last-macros'
    const prodGenerate = 'https://calorie-tracker-xr.up.railway.app/api/generate'
    const prodAddMacro = 'https://calorie-tracker-xr.up.railway.app/api/add-macro'

    var [totalCalorie, setTotalCalorie] = useState(0);
    var [totalProtein, setTotalProtein] = useState(0);
    var [totalCarbs, setTotalCarbs] = useState(0);
    var [totalFat, setTotalFat] = useState(0);

    const [tempMacro, setTempMacro] = useState(null);

    var [calorieProgressBar, setCalorieProgressBar] = useState(0);
    var [proteinProgressBar, setProteinProgressBar] = useState(0);
    var [carbsProgressBar, setCarbsProgressBar] = useState(0);
    var [fatProgressBar, setFatProgressBar] = useState(0);
    const [macros, setMacros] = useState(null);

    useEffect(() => {
        const token = localStorage.getItem("token");
        if (!token) {
          console.warn("No token found, user may not be logged in");
          logout();
          return;
        }
        // Load saved macros on initial load
        fetch(prodLast, {
            headers: {
                Authorization: `Bearer ${token}`
            }
        })
          .then(res => res.json())
          .then(data => {
            if ('msg' in data){
                logout();
            }
            if (!data.error) {
                setMacros(data);

                setTotalCalorie(data.targetCalorie);
                setTotalProtein(data.targetProtein);
                setTotalCarbs(data.targetCarbs);
                setTotalFat(data.targetFat);

                setCalorieProgressBar(data.calorie === 0 ? 0 : data.calorie * 100 / totalCalorie);
                setProteinProgressBar(data.protein === 0 ? 0 : data.protein * 100 / totalProtein);
                setCarbsProgressBar(data.carbs === 0 ? 0 : data.carbs * 100 / totalCarbs);
                setFatProgressBar(data.fat === 0 ? 0 : data.fat * 100 / totalFat);
            }})
          .catch(err => {
            console.error('Failed to fetch macros', err);
        });
      }, [token, logout, totalCalorie, totalProtein, totalCarbs, totalFat]);

  
    const handleUpload = async (event) => {
      let file = event.target.files[0];
      if (!file) return;
  
      let formData = new FormData();
      formData.append('image', file);
  
      try {
        const res = await fetch(prodGenerate, {
            headers: {
                Authorization: `Bearer ${token}`
            },
            method: 'POST',
            body: formData,
        });
  
        const data = await res.json();

        if (data.error) {
            setTempMacro(null)
            alert(data.error);
          } else {
            setTempMacro(data)
            console.log(tempMacro)
            
            formData = null
            file = null
          }
      } catch (err) {
        console.error('Upload error:', err);
      }
    };

    const addMacro = () => {
        let formData = new FormData();
        formData.append('data', tempMacro);
    
        fetch(prodAddMacro, {
            headers: {
                Authorization: `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            method: 'POST',
            body: JSON.stringify({tempMacro}),
        })
          .then(res => res.json())
          .then(data => {
            if (!data.error) {
                setTempMacro(null)
                setMacros(data);
                setCalorieProgressBar(data.calorie * 100 / totalCalorie);
                setProteinProgressBar(data.protein * 100 / totalProtein);
                setCarbsProgressBar(data.carbs * 100 / totalCarbs);
                setFatProgressBar(data.fat * 100 / totalFat);
            }})
          .catch(err => {
            console.error('Failed to fetch macros', err);
        });
      };

  return (
    <div class="background">


        {tempMacro && (
            <div className="body">
                <div id='temp-macro-container'>
                    <div id='temp-macro-info'>
                        <div className='temp-macro-info-row'> Calorie: {tempMacro.calorie}</div>
                        <div className='temp-macro-info-row'> Protein: {tempMacro.protein + 'g'}</div>
                        <div className='temp-macro-info-row'> Carbs: {tempMacro.carbs + 'g'}</div>
                        <div className='temp-macro-info-row'> Fat: {tempMacro.fat + 'g'}</div>
                    </div>

                    <div id='temp-macro-option'>
                        <div className='temp-macro-option-column' id='cancel' onClick={() => setTempMacro(null)}> Cancel </div>
                        <div className='temp-macro-option-column' id='add' onClick={addMacro}> Add </div>
                    </div>
                </div>
            </div>
        )}

        {!tempMacro && (

        <div className="body">
            {/* <button class="logout headerItem" style={{position: 'relative', top: '80vh', left:'20px'}} onClick={resetMacros}> ø </button> */}
            <div class="header">
                <div id="uploadRow">
                    <div class="upload">
                        <label for="file" class="btn">+</label>
                        <input  id="file" type="file" style={{color: 'transparent', display:"none"}} accept="image/*" onChange={handleUpload} />
                    </div>
                </div>
                <div id="logoutRow">
                    <button class="logout" onClick={logout}> Logout </button>
                </div>
            </div>

            <div class="mainBody">
                <div class="macro">
                    <div id="macroTitle"> Macro </div>
                    <div class="macro-bar"> 
                        <div class="macro-stats">
                            {macros && (
                                <div>
                                    <div class="stat" style={{color: Math.round(calorieProgressBar) > 120 ? "red" : Math.round(calorieProgressBar) > 100 ? "orange" : "black"}}> Calorie: {macros.calorie + "/" + totalCalorie}</div>
                                    <div class="stat" style={{color: Math.round(proteinProgressBar) > 120 ? "red" : Math.round(proteinProgressBar) > 100 ? "orange" : "black"}}> Protein: {macros.protein + "/" + totalProtein}</div>
                                    <div class="stat" style={{color: Math.round(carbsProgressBar) > 120 ? "red" : Math.round(carbsProgressBar) > 100 ? "orange" : "black"}}> Carbs: {macros.carbs + "/" + totalCarbs}</div>
                                    <div class="stat" style={{color: Math.round(fatProgressBar) > 120 ? "red" : Math.round(fatProgressBar) > 100 ? "orange" : "black"}}> Fat: {macros.fat + "/" + totalFat}</div>
                                </div>
                            )}
                            {!macros && (
                                <div>
                                    <div class="stat" style={{color: "black"}}> Calorie: {0 + "/" + totalCalorie}</div>
                                    <div class="stat" style={{color: "black"}}> Protein: {0 + "/" + totalProtein}</div>
                                    <div class="stat" style={{color: "black"}}> Carbs: {0 + "/" + totalCarbs}</div>
                                    <div class="stat" style={{color: "black"}}> Fat: {0 + "/" + totalFat}</div>
                                </div>
                            )}
                        </div>
                        
                        <div class="macro-chart"> 
                            <MacroHistoryChart token={token}></MacroHistoryChart>    
                        </div>
                    </div>
                </div>
            </div>
            
            <div id="rowTable">
                <div class="row">
                    <div class="info" id="Calorie">
                        <div class="homeCategory"> Calorie </div>
                        <div class="progress">
                            <div class="progressBar" style={{width: calorieProgressBar + '%'}}> {Math.round(calorieProgressBar) + '%'}  </div>
                        </div>
                    </div>
                    <div class="info" id="Protein">
                        <div class="homeCategory"> Protein </div>
                        <div class="progress">
                            <div class="progressBar" style={{width: proteinProgressBar + '%'}}> {Math.round(proteinProgressBar) + '%'} </div>
                        </div>
                    </div>
                </div>

                <div class="row">
                    <div class="info" id="Carbs">
                        <div class="homeCategory"> Carbs </div>
                        <div class="progress">
                            <div class="progressBar" style={{width: carbsProgressBar + '%'}}> {Math.round(carbsProgressBar) + '%'} </div>
                        </div>
                    </div>
                    <div class="info" id="Fat">
                        <div class="homeCategory"> Fat </div>
                        <div class="progress">
                            <div class="progressBar" style={{width: fatProgressBar + '%'}}> {Math.round(fatProgressBar) + '%'} </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>)}

    </div>
  );
}

export default HomePage;

