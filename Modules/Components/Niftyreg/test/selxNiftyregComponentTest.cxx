/*=========================================================================
 *
 *  Copyright Leiden University Medical Center, Erasmus University Medical
 *  Center and contributors
 *
 *  Licensed under the Apache License, Version 2.0 (the "License");
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *
 *        http://www.apache.org/licenses/LICENSE-2.0.txt
 *
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 *
 *=========================================================================*/

#include "selxSuperElastixFilter.h"
#include "selxRegistrationController.h"

#include "selxNiftyregReadImageComponent.h"
#include "selxNiftyregf3dComponent.h"
#include "selxDataManager.h"
#include "gtest/gtest.h"

namespace selx
{

class NiftyregComponentTest : public ::testing::Test
{
public:
  
    typedef std::shared_ptr< Blueprint >                        BlueprintPointer;
  typedef itk::SharedPointerDataObjectDecorator< Blueprint >  BlueprintITKType;
  typedef BlueprintITKType::Pointer                           BlueprintITKPointer;
  typedef Blueprint::ParameterMapType   ParameterMapType;
  typedef Blueprint::ParameterValueType ParameterValueType;
  typedef DataManager                   DataManagerType;

  /** register all example components */
  typedef TypeList< Niftyregf3dComponent<float>, NiftyregReadImageComponent<float>,
    RegistrationControllerComponent< > > RegisterComponents;

  typedef SuperElastixFilter< RegisterComponents >  SuperElastixFilterType;
  

  virtual void SetUp()
  {
  }


  virtual void TearDown()
  {
        itk::ObjectFactoryBase::UnRegisterAllFactories();
  }
    BlueprintPointer blueprint;
};

TEST_F( NiftyregComponentTest, Create )
{
    /** make example blueprint configuration */
  BlueprintPointer blueprint = BlueprintPointer( new Blueprint() );
  blueprint->SetComponent( "FixedImage", { { "NameOfClass", { "NiftyregReadImageComponent" } } });

   // Instantiate SuperElastix
  SuperElastixFilterType::Pointer superElastixFilter;
  EXPECT_NO_THROW( superElastixFilter = SuperElastixFilterType::New() );

  // Data manager provides the paths to the input and output data for unit tests
  DataManagerType::Pointer dataManager = DataManagerType::New();

  BlueprintITKPointer superElastixFilterBlueprint = BlueprintITKType::New();
  superElastixFilterBlueprint->Set( blueprint );
  EXPECT_NO_THROW( superElastixFilter->SetBlueprint( superElastixFilterBlueprint ) );

  //nifti_image *referenceImage=NULL;
  //nifti_image *floatingImage=NULL;
  //reg_f3d<float>* REG=new reg_f3d<float>(referenceImage->nt,floatingImage->nt);
}
}