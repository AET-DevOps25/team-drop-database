import React from 'react';
import { useParams } from 'react-router-dom';
import AttractionDetails from '../components/attractions/AttractionDetails';

type AttractionId = '1' | '2';

const Attraction: React.FC = () => {
  const { id } = useParams<{ id: AttractionId }>();

  if (!id) {
    return <div>未找到景点ID</div>;
  }

  return (
    <div>
      <AttractionDetails attractionId={id} />
    </div>
  );
};

export default Attraction;