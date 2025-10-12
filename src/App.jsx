import React, { useState, useEffect } from "react";
import "./App.css";

const initialRooms = {
  Hall: { lights: [false, false], fans: [0, 0], ac: null, heater: null, tv: false },
  Bedroom: { light: false, fan: 0, ac: null, heater: null },
  Kitchen: { light: false, fan: 0 },
  Bathroom: { light: false, geezer: null },
  Toilet: { light: false }
};

// Power ratings in watts
const powerRatings = {
  light: 15,
  fanSpeed: 40,
  ac: 1500,
  heater: 2000,
  tv: 100,
  geezer: 1500
};

// API keys
const EM_API_KEY = "2cydsXA6q2R9UUTgj9nx"; // ElectricityMaps
const VC_API_KEY = "6CUK6MHKK9V693T3CZ65Z89BJ"; // Visual Crossing
const LOCATION = "Mumbai,IN"; // Change to your city

function App() {
  const [rooms, setRooms] = useState(initialRooms);
  const [indoorTemp, setIndoorTemp] = useState(25);
  const [outdoorTemp, setOutdoorTemp] = useState(30);
  const [totalLoad, setTotalLoad] = useState(0);
  const [currentTime, setCurrentTime] = useState(new Date());
  const [tariff, setTariff] = useState(6); // fallback ₹6/kWh if API fails

  // Fetch electricity tariff from ElectricityMaps API
  useEffect(() => {
    const fetchTariff = async () => {
      try {
        const response = await fetch(
          "https://api.electricitymap.org/v3/carbon-intensity/latest?zone=IN",
          { headers: { "auth-token": EM_API_KEY } }
        );
        const data = await response.json();
        if (data?.carbonIntensity) {
          const dynamicTariff = (data.carbonIntensity * 0.01).toFixed(2);
          setTariff(Number(dynamicTariff));
        }
      } catch (err) {
        console.error("Failed to fetch tariff:", err);
      }
    };
    fetchTariff();
    const interval = setInterval(fetchTariff, 60000); // update every 1 min
    return () => clearInterval(interval);
  }, []);

  // Real-time clock updater
  useEffect(() => {
    const timeInterval = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timeInterval);
  }, []);

  // Fetch outdoor temperature from Visual Crossing API
  useEffect(() => {
    const fetchWeather = async () => {
      try {
        const response = await fetch(
          `https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/${LOCATION}/today?unitGroup=metric&key=${VC_API_KEY}&include=current`
        );
        const data = await response.json();
        if (data?.currentConditions?.temp) {
          setOutdoorTemp(data.currentConditions.temp);
        }
      } catch (err) {
        console.error("Failed to fetch outdoor temperature:", err);
      }
    };
    fetchWeather();
    const interval = setInterval(fetchWeather, 600000); // update every 10 min
    return () => clearInterval(interval);
  }, []);

  // Indoor temperature simulation
  useEffect(() => {
    const interval = setInterval(() => {
      let newIndoor = indoorTemp;
      Object.values(rooms).forEach(r => {
        if (r.ac) newIndoor += (r.ac - newIndoor) * 0.02;
        if (r.heater) newIndoor += (r.heater - newIndoor) * 0.02;
        if (r.fans) {
          const totalSpeed = Array.isArray(r.fans) ? r.fans.reduce((a, b) => a + b, 0) : r.fans;
          newIndoor -= 0.05 * totalSpeed;
        }
      });
      setIndoorTemp(Math.min(35, Math.max(15, newIndoor)));
    }, 200);
    return () => clearInterval(interval);
  }, [rooms, indoorTemp]);

  // Calculate load dynamically
  useEffect(() => {
    let total = 0;
    Object.values(rooms).forEach(room => {
      if (room.lights) total += room.lights.filter(Boolean).length * powerRatings.light;
      if (room.light) total += room.light ? powerRatings.light : 0;

      if (room.fans) total += room.fans.reduce((sum, s) => sum + s * powerRatings.fanSpeed, 0);
      if (room.fan) total += room.fan * powerRatings.fanSpeed;

      if (room.ac) total += powerRatings.ac;
      if (room.heater) total += powerRatings.heater;
      if (room.tv) total += powerRatings.tv;
      if (room.geezer) total += powerRatings.geezer;
    });
    setTotalLoad(total);
  }, [rooms]);

  // Device control functions
  const toggleLight = (roomName, idx = null) => {
    setRooms(prev => {
      const room = { ...prev[roomName] };
      if (idx !== null) {
        room.lights = [...room.lights];
        room.lights[idx] = !room.lights[idx];
      } else {
        room.light = !room.light;
      }
      return { ...prev, [roomName]: room };
    });
  };

  const changeFan = (roomName, idx = null, delta = 1) => {
    setRooms(prev => {
      const room = { ...prev[roomName] };
      if (idx !== null) {
        room.fans = [...room.fans];
        room.fans[idx] = delta === 0 ? 0 : Math.min(3, room.fans[idx] + delta);
      } else {
        room.fan = delta === 0 ? 0 : Math.min(3, room.fan + delta);
      }
      return { ...prev, [roomName]: room };
    });
  };

  const changeTemp = (roomName, key, delta) => {
    setRooms(prev => {
      const room = { ...prev[roomName] };
      if (room[key] === null) room[key] = key === "ac" ? 26 : 22;
      else {
        if (key === "ac") room[key] = Math.max(18, Math.min(30, room[key] + delta));
        else room[key] = Math.max(20, Math.min(35, room[key] + delta));
      }
      return { ...prev, [roomName]: room };
    });
  };

  const turnOff = (roomName, key) => setRooms(prev => ({ ...prev, [roomName]: { ...prev[roomName], [key]: null } }));
  const toggleTV = (roomName) => setRooms(prev => ({ ...prev, [roomName]: { ...prev[roomName], tv: !prev[roomName].tv } }));
  const toggleGeezer = (roomName) => setRooms(prev => ({
    ...prev,
    [roomName]: { ...prev[roomName], geezer: prev[roomName].geezer ? null : 60 }
  }));

  const totalKW = (totalLoad / 1000).toFixed(2);
  const costPerHour = (totalKW * tariff).toFixed(2);
  const formattedTime = currentTime.toLocaleTimeString();

  return (
    <div className="App">
      <h1>🏠 1BHK Smart Home Simulation</h1>

      <p className="status-bar">
        🕒 {formattedTime} | 🌡 Indoor: {indoorTemp.toFixed(1)}°C | ☀️ Outdoor: {outdoorTemp.toFixed(1)}°C
      </p>

      <h3>
        ⚡ Total Load: {totalLoad} W ({totalKW} kW) | 💰 Cost per hour: ₹{costPerHour} | 🪙 Tariff: ₹{tariff}/kWh
      </h3>

      <div className="grid-container">
        {Object.entries(rooms).map(([name, devices]) => (
          <Room
            key={name}
            name={name}
            devices={devices}
            toggleLight={toggleLight}
            changeFan={changeFan}
            changeTemp={changeTemp}
            turnOff={turnOff}
            toggleTV={toggleTV}
            toggleGeezer={toggleGeezer}
          />
        ))}
      </div>
    </div>
  );
}

// Room component
function Room({ name, devices, toggleLight, changeFan, changeTemp, turnOff, toggleTV, toggleGeezer }) {
  return (
    <div className="room">
      <h2>{name}</h2>
      <div className="devices">
        {devices.lights?.map((on, idx) => (
          <div key={idx} className="device-box">
            <div>Light {idx + 1}: {on ? "ON" : "OFF"}</div>
            <div className={`light ${on ? "on" : "off"}`} />
            <button onClick={() => toggleLight(name, idx)}>Toggle Light</button>
          </div>
        ))}
        {devices.light !== undefined && (
          <div className="device-box">
            <div>Light: {devices.light ? "ON" : "OFF"}</div>
            <div className={`light ${devices.light ? "on" : "off"}`} />
            <button onClick={() => toggleLight(name)}>Toggle Light</button>
          </div>
        )}

        {devices.fans?.map((speed, idx) => (
          <div key={idx} className="fan-container">
            <SVGFan speed={speed} />
            <button onClick={() => changeFan(name, idx, +1)}>Fan +</button>
            <button onClick={() => changeFan(name, idx, 0)}>Off</button>
          </div>
        ))}
        {devices.fan !== undefined && (
          <div className="fan-container">
            <SVGFan speed={devices.fan} />
            <button onClick={() => changeFan(name, null, +1)}>Fan +</button>
            <button onClick={() => changeFan(name, null, 0)}>Off</button>
          </div>
        )}

        {devices.ac !== undefined && (
          <div className="device-box ac">
            <div>AC: {devices.ac ?? "Off"}</div>
            <button onClick={() => changeTemp(name, "ac", +1)}>AC ↑</button>
            <button onClick={() => changeTemp(name, "ac", -1)}>AC ↓</button>
            <button onClick={() => turnOff(name, "ac")}>Off</button>
          </div>
        )}
        {devices.heater !== undefined && (
          <div className="device-box heater">
            <div>Heater: {devices.heater ?? "Off"}</div>
            <button onClick={() => changeTemp(name, "heater", +1)}>Heater ↑</button>
            <button onClick={() => changeTemp(name, "heater", -1)}>Heater ↓</button>
            <button onClick={() => turnOff(name, "heater")}>Off</button>
          </div>
        )}

        {devices.tv !== undefined && (
          <div className={`device-box tv ${devices.tv ? "on" : "off"}`}>
            <div>TV: {devices.tv ? "ON" : "OFF"}</div>
            <button onClick={() => toggleTV(name)}>Toggle TV</button>
          </div>
        )}

        {devices.geezer !== undefined && (
          <div className={`device-box geezer ${devices.geezer ? "on" : "off"}`}>
            <div>Geezer: {devices.geezer ? "ON" : "OFF"}</div>
            <button onClick={() => toggleGeezer(name)}>Toggle Geezer</button>
          </div>
        )}
      </div>
    </div>
  );
}

// Fan SVG
function SVGFan({ speed }) {
  return (
    <svg className={`fan-svg fan-speed-${speed}`} width="50" height="50" viewBox="0 0 50 50">
      <circle cx="25" cy="25" r="5" fill="cyan" />
      <line x1="25" y1="25" x2="25" y2="5" stroke="cyan" strokeWidth="3" />
      <line x1="25" y1="25" x2="45" y2="25" stroke="cyan" strokeWidth="3" />
      <line x1="25" y1="25" x2="25" y2="45" stroke="cyan" strokeWidth="3" />
      <line x1="25" y1="25" x2="5" y2="25" stroke="cyan" strokeWidth="3" />
    </svg>
  );
}

export default App;
