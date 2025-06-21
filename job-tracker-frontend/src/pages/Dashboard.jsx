import StickyHeadTable from '../components/StickyHeadTable';
import AutoTopBoard, { fetchCounts } from '../components/AutoTopBoard';
import { useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import axios from 'axios';
import PrimarySearchAppBar from '../components/Navbar'



export default function Dashboard() {
    console.log("DASHBOARD RENDERED");
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate()

    useEffect(()=>{
      const token = localStorage.getItem('token');

      if (!token) {
        console.log('❌ No token found');
        navigate('/Login');
        return;
      }

      axios.get('http://localhost:8080/api/authcheck', {
        headers: {
          Authorization: token,
        },
        withCredentials: true,
      })
      .then(res => {
        if (!res.data.authenticated) {
          navigate('/Login');
        } else {
          console.log('✅ AUTH RESPONSE:', res.data);
          setLoading(false);
        }
      })
      .catch((err) => {
        console.error('Not Logged-In');
        navigate('/Login');
      });
  }, []);

  if (loading) return <div>Loading...</div>;

    return (
      <div className="center-screen">
        <PrimarySearchAppBar/>

        <h1>DASHBOARD</h1>
        <AutoTopBoard/>
        <div style={{ width: '80%' }}>
    <h2 className="left-heading">Recent Applications</h2>
  </div>
        <StickyHeadTable onUpdateCounts={fetchCounts} />
      </div>
    );
  }
