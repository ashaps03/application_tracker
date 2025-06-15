import StickyHeadTable from '../components/StickyHeadTable';
import AutoTopBoard, { fetchCounts } from '../components/AutoTopBoard';
import SignOut from '../components/SignOut';

export default function Dashboard() {
    console.log("DASHBOARD RENDERED");
  
    return (
      <div className="center-screen">
        <div>
        <SignOut/>
        </div>
        <h1>DASHBOARD</h1>
        <AutoTopBoard/>
        <div style={{ width: '80%' }}>
    <h2 className="left-heading">Recent Applications</h2>
  </div>
        <StickyHeadTable onUpdateCounts={fetchCounts} />
      </div>
    );
  }
